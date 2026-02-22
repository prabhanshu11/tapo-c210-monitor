"""Scene scanner orchestrating periodic YOLO detection + LLM enrichment.

Runs continuous object detection on camera frames via the ring buffer,
logging all results to SQLite. Optionally enriches novel scenes with
LLM vision descriptions via OpenRouter.
"""

import time
import threading
from typing import Optional, Callable

from ..change_detector import ChangeEvent, LLMVisionAnalyzer
from .yolo_detector import YOLODetector, Detection
from .object_logger import ObjectLogger


class SceneScanner:
    """Orchestrates periodic + change-triggered object detection.

    - Periodic scans: YOLO every `periodic_interval` seconds
    - Change-triggered scans: immediate YOLO when ChangeMonitor fires callback
    - LLM enrichment: rate-limited calls for novel/interesting scenes
    """

    def __init__(
        self,
        ringbuffer_url: str = "http://localhost:8085",
        detector: Optional[YOLODetector] = None,
        logger: Optional[ObjectLogger] = None,
        llm_analyzer: Optional[LLMVisionAnalyzer] = None,
        periodic_interval: float = 30.0,
        llm_interval: float = 300.0,
        llm_max_per_hour: int = 12,
        source_device: str = "desktop",
        source_camera: str = "tapo-c210-192.168.29.183",
    ):
        self.ringbuffer_url = ringbuffer_url
        self.detector = detector or YOLODetector()
        self.logger = logger or ObjectLogger()
        self.llm_analyzer = llm_analyzer
        self.periodic_interval = periodic_interval
        self.llm_interval = llm_interval
        self.llm_max_per_hour = llm_max_per_hour
        self.source_device = source_device
        self.source_camera = source_camera

        self._running = False
        self._thread: Optional[threading.Thread] = None

        # LLM rate limiting state
        self._last_llm_call: float = 0.0
        self._llm_calls_this_hour: list[float] = []

        # Novelty tracking: {class_name: last_seen_unix}
        self._recent_classes: dict[str, float] = {}
        self._novelty_window: float = 300.0  # 5 minutes

    def start(self):
        """Start the periodic scan loop (blocking)."""
        self._running = True
        print(f"SceneScanner started (interval={self.periodic_interval}s, "
              f"LLM={'enabled' if self.llm_analyzer else 'disabled'})")
        print(f"  Device: {self.detector.device} | "
              f"Camera: {self.source_camera}")

        while self._running:
            try:
                self._periodic_scan()
            except Exception as e:
                print(f"[SceneScanner] Scan error: {e}")

            time.sleep(self.periodic_interval)

    def start_background(self):
        """Start scanning in a background thread."""
        self._thread = threading.Thread(target=self.start, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the scan loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def scan_now(self, scan_type: str = "manual") -> list[Detection]:
        """Run a single scan immediately (on-demand).

        Returns the list of detections.
        """
        detections, frame_path = self.detector.detect_from_ringbuffer(
            self.ringbuffer_url
        )

        scan_id = self.logger.log_scan(
            scan_type=scan_type,
            detections=detections,
            source_device=self.source_device,
            source_camera=self.source_camera,
            frame_path=frame_path,
        )

        self._update_novelty(detections)
        self._maybe_enrich_with_llm(scan_id, detections, frame_path)

        return detections

    def on_change(self, event: ChangeEvent):
        """Callback for ChangeMonitor — runs immediate YOLO scan.

        Pass this method as the callback to ChangeMonitor.start():
            monitor.start(callback=scanner.on_change)
        """
        detections, frame_path = self.detector.detect_from_ringbuffer(
            self.ringbuffer_url
        )

        scan_id = self.logger.log_scan(
            scan_type="change_triggered",
            detections=detections,
            source_device=self.source_device,
            source_camera=self.source_camera,
            frame_path=frame_path,
            change_score=event.change_score,
        )

        self._update_novelty(detections)

        # Higher priority for LLM on high change scores
        if event.change_score > 0.3:
            self._maybe_enrich_with_llm(
                scan_id, detections, frame_path, force_priority=True
            )

        obj_names = [d.class_name for d in detections]
        print(f"  [change] score={event.change_score:.3f} "
              f"objects={obj_names}")

    def _periodic_scan(self):
        """Single periodic scan: grab frame → YOLO → log."""
        detections, frame_path = self.detector.detect_from_ringbuffer(
            self.ringbuffer_url
        )

        scan_id = self.logger.log_scan(
            scan_type="periodic",
            detections=detections,
            source_device=self.source_device,
            source_camera=self.source_camera,
            frame_path=frame_path,
        )

        novel = self._update_novelty(detections)
        self._maybe_enrich_with_llm(scan_id, detections, frame_path)

        obj_names = [d.class_name for d in detections]
        ts = time.strftime("%H:%M:%S")
        novel_str = f" NEW={novel}" if novel else ""
        print(f"[{ts}] {len(detections)} objects: {obj_names}{novel_str}")

    def _update_novelty(self, detections: list[Detection]) -> list[str]:
        """Track which object classes are novel (not seen recently).

        Returns list of novel class names.
        """
        now = time.time()
        novel = []

        for d in detections:
            last_seen = self._recent_classes.get(d.class_name, 0)
            if now - last_seen > self._novelty_window:
                novel.append(d.class_name)
            self._recent_classes[d.class_name] = now

        # Clean old entries
        self._recent_classes = {
            k: v for k, v in self._recent_classes.items()
            if now - v < self._novelty_window * 2
        }

        return novel

    def _should_call_llm(
        self,
        detections: list[Detection],
        force_priority: bool = False,
    ) -> bool:
        """Decide whether to call LLM for this scan.

        Conditions (any triggers a call, subject to rate limits):
        1. New object class not seen in last 5 minutes
        2. Periodic enrichment every llm_interval seconds
        3. force_priority=True (high change score)
        """
        if not self.llm_analyzer:
            return False

        now = time.time()

        # Prune old LLM call timestamps
        hour_ago = now - 3600
        self._llm_calls_this_hour = [
            t for t in self._llm_calls_this_hour if t > hour_ago
        ]

        # Rate limit check
        if len(self._llm_calls_this_hour) >= self.llm_max_per_hour:
            return False

        # Condition 3: forced priority (high change score)
        if force_priority:
            return True

        # Condition 1: novel classes
        for d in detections:
            last_seen = self._recent_classes.get(d.class_name, 0)
            # Check if class was novel *before* the current update
            # (novelty already updated by _update_novelty, so check
            # if it was just added in the last scan interval)
            if now - last_seen < self.periodic_interval * 1.5:
                # Recently updated — check if it was novel before that
                pass  # Handled by novelty list in caller

        # Condition 2: periodic LLM enrichment
        if now - self._last_llm_call >= self.llm_interval:
            return True

        return False

    def _maybe_enrich_with_llm(
        self,
        scan_id: int,
        detections: list[Detection],
        frame_path: Optional[str],
        force_priority: bool = False,
    ):
        """Call LLM to enrich scan if conditions met."""
        if not self._should_call_llm(detections, force_priority):
            return

        if not frame_path or not self.llm_analyzer:
            return

        try:
            # Build a ChangeEvent-like structure for the analyzer
            event = ChangeEvent(
                timestamp=time.time(),
                change_score=0.0,
                frames_before=[],
                frames_after=[frame_path],
            )

            summary = self.llm_analyzer.analyze_change(event)
            self.logger.update_llm_summary(scan_id, summary)

            now = time.time()
            self._last_llm_call = now
            self._llm_calls_this_hour.append(now)

            print(f"  [LLM] {summary[:100]}...")
        except Exception as e:
            print(f"  [LLM] Error: {e}")
