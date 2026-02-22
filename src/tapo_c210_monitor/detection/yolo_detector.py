"""YOLO-based object detection for camera frames.

Uses YOLOv8 (ultralytics) with CUDA acceleration for real-time
detection of 80 COCO object classes.
"""

import numpy as np
import httpx
from pathlib import Path
from dataclasses import dataclass
from ultralytics import YOLO


@dataclass
class Detection:
    """A single detected object in a frame."""
    class_name: str        # "person", "laptop", "cup"
    class_id: int          # COCO class ID
    confidence: float      # 0.0-1.0
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2
    frame_width: int
    frame_height: int


class YOLODetector:
    """Wraps ultralytics YOLOv8 for object detection on camera frames.

    Model is loaded once on init and kept warm in GPU memory.
    YOLOv8n (~6MB) auto-downloads on first run.
    """

    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        confidence_threshold: float = 0.25,
        device: str | None = None,
    ):
        self.model = YOLO(model_name)
        self.confidence_threshold = confidence_threshold

        # Auto-detect CUDA, fall back to CPU
        if device is None:
            import torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Warm up model on device
        self.model.to(self.device)

    def detect(self, frame: np.ndarray | str | Path) -> list[Detection]:
        """Run object detection on a frame.

        Args:
            frame: numpy array (BGR from OpenCV), or path to image file.

        Returns:
            List of Detection objects found in the frame.
        """
        results = self.model(
            frame,
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False,
        )

        if not results:
            return []

        result = results[0]
        detections = []

        # Get frame dimensions from result
        h, w = result.orig_shape

        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append(Detection(
                class_name=result.names[int(box.cls[0])],
                class_id=int(box.cls[0]),
                confidence=float(box.conf[0]),
                bbox=(int(x1), int(y1), int(x2), int(y2)),
                frame_width=w,
                frame_height=h,
            ))

        return detections

    def detect_from_ringbuffer(
        self,
        ringbuffer_url: str = "http://localhost:8085",
        seconds_ago: float = 0,
        output_dir: str = "/tmp/yolo_frames",
    ) -> tuple[list[Detection], str | None]:
        """Grab a frame from the ring buffer and run detection.

        Returns:
            Tuple of (detections, frame_path). frame_path is None if
            frame extraction failed.
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        resp = httpx.get(
            f"{ringbuffer_url}/frames",
            params={
                "seconds_ago": str(seconds_ago),
                "output_dir": output_dir,
            },
            timeout=30,
        )
        resp.raise_for_status()
        frames = resp.json().get("frames", [])

        if not frames:
            return [], None

        frame_path = frames[0]
        detections = self.detect(frame_path)
        return detections, frame_path
