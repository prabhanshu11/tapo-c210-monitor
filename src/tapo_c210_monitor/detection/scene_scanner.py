"""Active Scene Manager — camera-aware object detection with temporal tracking.

Priority-based control loop:
  1. INVESTIGATE — pan toward edge detections or change events
  2. SWEEP — periodic coverage of multiple PTZ positions
  3. SCAN — routine YOLO detection at current position

Replaces the passive SceneScanner with PTZ-aware autonomous monitoring.
"""

import time
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from ..change_detector import ChangeEvent, LLMVisionAnalyzer
from ..onvif_ptz import TapoPTZ, PTZPosition
from .yolo_detector import YOLODetector, Detection
from .object_logger import ObjectLogger
from .frame_store import FrameStore


# 5-position cross pattern for coverage sweeps
SWEEP_POSITIONS = [
    (0.0, 0.0),    # center (home)
    (-0.8, 0.0),   # left
    (0.8, 0.0),    # right
    (0.0, -0.3),   # up
    (0.0, 0.3),    # down
]

EDGE_MARGIN = 80  # pixels from frame boundary to trigger investigation


@dataclass
class InvestigationTarget:
    """A pending investigation — something detected at frame edge."""
    direction_pan: float   # relative pan adjustment
    direction_tilt: float  # relative tilt adjustment
    source_class: str
    source_confidence: float
    source_position: tuple[float, float]  # camera pan, tilt when detected
    created_at: float = field(default_factory=time.time)


class ActiveSceneManager:
    """Autonomous scene monitoring with PTZ control and temporal tracking.

    Modes:
    - Passive (no PTZ): scans current view periodically, tracks objects.
    - Active (with PTZ): sweeps positions, investigates edge detections,
      maintains coverage log.
    """

    def __init__(
        self,
        ringbuffer_url: str = "http://localhost:8085",
        detector: Optional[YOLODetector] = None,
        logger: Optional[ObjectLogger] = None,
        ptz: Optional[TapoPTZ] = None,
        llm_analyzer: Optional[LLMVisionAnalyzer] = None,
        frame_store: Optional[FrameStore] = None,
        scan_interval: float = 30.0,
        sweep_interval: float = 300.0,
        settle_time: float = 3.0,
        home_position: tuple[float, float] = (0.0, 0.0),
        source_device: str = "desktop",
        source_camera: str = "tapo-c210-192.168.50.199",
    ):
        self.ringbuffer_url = ringbuffer_url
        self.detector = detector or YOLODetector()
        self.logger = logger or ObjectLogger()
        self.ptz = ptz
        self.llm_analyzer = llm_analyzer
        self.frame_store = frame_store
        self.scan_interval = scan_interval
        self.sweep_interval = sweep_interval
        self.settle_time = settle_time
        self.home_position = home_position
        self.source_device = source_device
        self.source_camera = source_camera

        self._running = False
        self._investigation_queue: deque[InvestigationTarget] = deque(maxlen=10)
        self._last_sweep: float = 0.0
        self._last_cleanup: float = 0.0
        self._current_position: tuple[float, float] = home_position
        self._seen_classes_today: set[str] = set()
        self._day_marker: str = time.strftime("%Y-%m-%d")

        # LLM rate limiting
        self._last_llm_call: float = 0.0
        self._llm_calls_this_hour: list[float] = []
        self._llm_max_per_hour: int = 12
        self._llm_interval: float = 300.0

    # ── Public API ────────────────────────────────────────────────

    def start(self):
        """Main control loop (blocking)."""
        self._running = True
        ptz_label = "PTZ enabled" if self.ptz else "passive (no PTZ)"
        print(f"[ActiveSceneManager] Started ({ptz_label}, "
              f"scan={self.scan_interval}s, sweep={self.sweep_interval}s)")
        print(f"  Device: {self.detector.device} | Camera: {self.source_camera}")

        while self._running:
            try:
                self._reset_daily_state()

                # Priority 1: Investigate edge detections
                if self.ptz and self._investigation_queue:
                    self._run_investigation()
                    continue

                # Priority 2: Coverage sweep
                if self.ptz and self._sweep_due():
                    self._run_sweep()
                    continue

                # Priority 3: Periodic scan at current position
                self._run_periodic_scan()

                # Periodic frame cleanup (every 30 min)
                if self.frame_store and time.time() - self._last_cleanup > 1800:
                    self.frame_store.cleanup(self.logger)
                    self._last_cleanup = time.time()

            except Exception as e:
                print(f"[ActiveSceneManager] Error: {e}")

            time.sleep(self.scan_interval)

    def stop(self):
        """Stop the control loop."""
        self._running = False

    def scan_now(self, scan_type: str = "manual") -> list[Detection]:
        """Run a single scan immediately."""
        detections, frame_path = self.detector.detect_from_ringbuffer(
            self.ringbuffer_url
        )
        pos = self._get_camera_position()

        scan_id = self.logger.log_scan(
            scan_type=scan_type,
            detections=detections,
            source_device=self.source_device,
            source_camera=self.source_camera,
            frame_path=frame_path,
            camera_pan=pos[0] if pos else None,
            camera_tilt=pos[1] if pos else None,
        )

        self._update_tracks(detections, scan_id, pos)
        return detections

    def on_change(self, event: ChangeEvent):
        """Callback for ChangeMonitor — runs immediate scan."""
        detections, frame_path = self.detector.detect_from_ringbuffer(
            self.ringbuffer_url
        )
        pos = self._get_camera_position()

        scan_id = self.logger.log_scan(
            scan_type="change_triggered",
            detections=detections,
            source_device=self.source_device,
            source_camera=self.source_camera,
            frame_path=frame_path,
            change_score=event.change_score,
            camera_pan=pos[0] if pos else None,
            camera_tilt=pos[1] if pos else None,
        )

        self._update_tracks(detections, scan_id, pos)

        if event.change_score > 0.3:
            self._maybe_enrich_with_llm(scan_id, detections, frame_path, force=True)

        obj_names = [d.class_name for d in detections]
        print(f"  [change] score={event.change_score:.3f} objects={obj_names}")

    # ── Control loop actions ──────────────────────────────────────

    def _run_investigation(self):
        """Investigate an edge detection: pan camera, scan, return."""
        target = self._investigation_queue.popleft()

        # Skip stale investigations (>60s old)
        if time.time() - target.created_at > 60:
            return

        previous_pos = self._current_position
        print(f"[investigate] {target.source_class} "
              f"(conf={target.source_confidence:.2f}) → "
              f"pan={target.direction_pan:+.1f} tilt={target.direction_tilt:+.1f}")

        # Move toward the detection
        target_pan = target.source_position[0] + target.direction_pan
        target_tilt = target.source_position[1] + target.direction_tilt
        self._move_to_position(target_pan, target_tilt)

        # Scan at investigation position
        detections, frame_path = self.detector.detect_from_ringbuffer(
            self.ringbuffer_url
        )
        pos = self._get_camera_position()

        retained = True  # Always retain investigation frames
        scan_id = self.logger.log_scan(
            scan_type="investigate",
            detections=detections,
            source_device=self.source_device,
            source_camera=self.source_camera,
            frame_path=frame_path,
            camera_pan=pos[0] if pos else None,
            camera_tilt=pos[1] if pos else None,
            frame_retained=retained,
        )

        self._update_tracks(detections, scan_id, pos)
        self._retain_frame(scan_id, frame_path, retained)
        self._maybe_enrich_with_llm(scan_id, detections, frame_path, force=True)

        obj_names = [d.class_name for d in detections]
        print(f"  [investigate result] {len(detections)} objects: {obj_names}")

        # Return to previous position
        self._move_to_position(*previous_pos)

    def _run_sweep(self):
        """Sweep through all coverage positions."""
        print(f"[sweep] Starting coverage sweep ({len(SWEEP_POSITIONS)} positions)")
        self._last_sweep = time.time()

        for i, (pan, tilt) in enumerate(SWEEP_POSITIONS):
            if not self._running:
                break

            self._move_to_position(pan, tilt)

            detections, frame_path = self.detector.detect_from_ringbuffer(
                self.ringbuffer_url
            )
            pos = self._get_camera_position()
            pan_actual = pos[0] if pos else pan
            tilt_actual = pos[1] if pos else tilt

            retained = self._should_retain_frame(detections, "sweep")
            scan_id = self.logger.log_scan(
                scan_type="sweep",
                detections=detections,
                source_device=self.source_device,
                source_camera=self.source_camera,
                frame_path=frame_path,
                camera_pan=pan_actual,
                camera_tilt=tilt_actual,
                frame_retained=retained,
            )

            self._update_tracks(detections, scan_id, (pan_actual, tilt_actual))
            self._retain_frame(scan_id, frame_path, retained)

            interesting = any(d.class_name == "person" for d in detections)
            self.logger.log_coverage(
                pan_actual, tilt_actual, len(detections), interesting
            )

            obj_names = [d.class_name for d in detections]
            marker = " *" if interesting else ""
            print(f"  [{i+1}/{len(SWEEP_POSITIONS)}] "
                  f"pan={pan_actual:.1f} tilt={tilt_actual:.1f} "
                  f"→ {obj_names}{marker}")

        # Return home
        self._move_to_position(*self.home_position)
        print(f"[sweep] Complete, returned to home")

    def _run_periodic_scan(self):
        """Single periodic scan at current position."""
        detections, frame_path = self.detector.detect_from_ringbuffer(
            self.ringbuffer_url
        )
        pos = self._get_camera_position()

        retained = self._should_retain_frame(detections, "periodic")
        scan_id = self.logger.log_scan(
            scan_type="periodic",
            detections=detections,
            source_device=self.source_device,
            source_camera=self.source_camera,
            frame_path=frame_path,
            camera_pan=pos[0] if pos else None,
            camera_tilt=pos[1] if pos else None,
            frame_retained=retained,
        )

        self._update_tracks(detections, scan_id, pos)
        self._retain_frame(scan_id, frame_path, retained)

        if self.ptz:
            self._check_edge_detections(detections, pos)

        self._maybe_enrich_with_llm(scan_id, detections, frame_path)

        obj_names = [d.class_name for d in detections]
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] {len(detections)} objects: {obj_names}")

    # ── PTZ helpers ───────────────────────────────────────────────

    def _move_to_position(self, target_pan: float, target_tilt: float):
        """Move camera to target position using timed continuous moves."""
        if not self.ptz:
            return

        current = self.ptz.get_position()
        if not current:
            # No position feedback — try absolute move directly
            self.ptz.absolute_move(target_pan, target_tilt)
            time.sleep(self.settle_time)
            self._current_position = (target_pan, target_tilt)
            return

        pan_diff = target_pan - current.pan
        tilt_diff = target_tilt - current.tilt

        # Skip tiny movements
        if abs(pan_diff) < 0.05 and abs(tilt_diff) < 0.05:
            self._current_position = (current.pan, current.tilt)
            return

        PAN_SPEED = 0.5
        TILT_SPEED = 0.5
        UNITS_PER_SECOND = 0.5

        pan_vel = PAN_SPEED if pan_diff > 0 else (-PAN_SPEED if pan_diff < 0 else 0)
        tilt_vel = TILT_SPEED if tilt_diff > 0 else (-TILT_SPEED if tilt_diff < 0 else 0)
        duration = max(abs(pan_diff), abs(tilt_diff)) / UNITS_PER_SECOND
        duration = min(duration, 4.0)  # cap at 4s to prevent runaway

        self.ptz.move_timed(pan_vel, tilt_vel, duration)
        time.sleep(self.settle_time)

        self._current_position = (target_pan, target_tilt)

    def _get_camera_position(self) -> Optional[tuple[float, float]]:
        """Get current camera position as (pan, tilt) or None."""
        if not self.ptz:
            return None
        pos = self.ptz.get_position()
        if pos:
            return (pos.pan, pos.tilt)
        return self._current_position if self.ptz else None

    def _sweep_due(self) -> bool:
        """Check if a coverage sweep is due."""
        return time.time() - self._last_sweep >= self.sweep_interval

    # ── Track management ──────────────────────────────────────────

    def _update_tracks(
        self,
        detections: list[Detection],
        scan_id: int,
        position: Optional[tuple[float, float]],
    ):
        """Match detections to tracks, update or create."""
        pan = position[0] if position else None
        tilt = position[1] if position else None

        matched_track_ids = set()
        for det in detections:
            track_id = self.logger.upsert_track(
                class_name=det.class_name,
                scan_id=scan_id,
                detection=det,
                camera_pan=pan,
                camera_tilt=tilt,
            )
            matched_track_ids.add(track_id)
            self._seen_classes_today.add(det.class_name)

        # Increment misses for active tracks at this position that weren't matched
        self.logger.increment_track_misses(pan, tilt)

    # ── Edge detection ────────────────────────────────────────────

    def _check_edge_detections(
        self,
        detections: list[Detection],
        position: Optional[tuple[float, float]],
    ):
        """Check if any detections are near frame edges → queue investigation."""
        if not position:
            return

        for d in detections:
            w, h = d.frame_width, d.frame_height
            at_left = d.bbox[0] < EDGE_MARGIN
            at_right = d.bbox[2] > w - EDGE_MARGIN
            at_top = d.bbox[1] < EDGE_MARGIN
            at_bottom = d.bbox[3] > h - EDGE_MARGIN

            if not (at_left or at_right or at_top or at_bottom):
                continue

            # Determine investigation direction (move camera toward the edge)
            dir_pan = 0.0
            dir_tilt = 0.0
            if at_left:
                dir_pan = -0.3
            elif at_right:
                dir_pan = 0.3
            if at_top:
                dir_tilt = -0.2
            elif at_bottom:
                dir_tilt = 0.2

            self._investigation_queue.append(InvestigationTarget(
                direction_pan=dir_pan,
                direction_tilt=dir_tilt,
                source_class=d.class_name,
                source_confidence=d.confidence,
                source_position=position,
            ))

            self.logger.log_edge_case(
                scan_id=0,  # scan_id already committed; we use the class info
                case_type="frame_edge",
                class_name=d.class_name,
                confidence=d.confidence,
                description=f"Object at {'left' if at_left else 'right' if at_right else 'top' if at_top else 'bottom'} edge",
            )

    # ── Frame retention ───────────────────────────────────────────

    def _should_retain_frame(
        self, detections: list[Detection], scan_type: str
    ) -> bool:
        """Decide if this frame is worth keeping."""
        if scan_type == "investigate":
            return True
        if any(d.class_name == "person" for d in detections):
            return True
        if any(d.class_name not in self._seen_classes_today for d in detections):
            return True
        return False

    def _retain_frame(
        self, scan_id: int, frame_path: Optional[str], retained: bool
    ):
        """Store frame if retained, update database."""
        if not frame_path or not retained or not self.frame_store:
            return
        stored_path = self.frame_store.store(frame_path, scan_id)
        self.logger.update_frame_retention(scan_id, stored_path, True)

    # ── LLM enrichment ────────────────────────────────────────────

    def _maybe_enrich_with_llm(
        self,
        scan_id: int,
        detections: list[Detection],
        frame_path: Optional[str],
        force: bool = False,
    ):
        """Call LLM to enrich scan if conditions met."""
        if not self.llm_analyzer or not frame_path:
            return

        now = time.time()

        # Prune old LLM call timestamps
        hour_ago = now - 3600
        self._llm_calls_this_hour = [
            t for t in self._llm_calls_this_hour if t > hour_ago
        ]

        if len(self._llm_calls_this_hour) >= self._llm_max_per_hour:
            return

        if not force and now - self._last_llm_call < self._llm_interval:
            return

        try:
            event = ChangeEvent(
                timestamp=now,
                change_score=0.0,
                frames_before=[],
                frames_after=[frame_path],
            )
            summary = self.llm_analyzer.analyze_change(event)
            self.logger.update_llm_summary(scan_id, summary)

            self._last_llm_call = now
            self._llm_calls_this_hour.append(now)
            print(f"  [LLM] {summary[:100]}...")
        except Exception as e:
            print(f"  [LLM] Error: {e}")

    # ── Daily state reset ─────────────────────────────────────────

    def _reset_daily_state(self):
        """Reset seen-classes tracker at midnight."""
        today = time.strftime("%Y-%m-%d")
        if today != self._day_marker:
            self._seen_classes_today.clear()
            self._day_marker = today


# Backward-compat alias
SceneScanner = ActiveSceneManager
