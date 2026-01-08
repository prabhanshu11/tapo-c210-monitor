"""RTSP stream capture and processing for TAPO C210."""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Generator, Callable
import threading
import time


class StreamCapture:
    """Capture and process RTSP video streams from TAPO C210."""

    def __init__(self, rtsp_url: str, reconnect_delay: float = 5.0):
        """Initialize stream capture.

        Args:
            rtsp_url: Full RTSP URL with credentials
            reconnect_delay: Seconds to wait before reconnection attempts
        """
        self.rtsp_url = rtsp_url
        self.reconnect_delay = reconnect_delay
        self._cap: cv2.VideoCapture | None = None
        self._running = False
        self._frame_callbacks: list[Callable[[np.ndarray], None]] = []
        self._capture_thread: threading.Thread | None = None
        self._last_frame: np.ndarray | None = None
        self._frame_lock = threading.Lock()

    def connect(self) -> bool:
        """Connect to RTSP stream.

        Returns:
            True if connection successful
        """
        self._cap = cv2.VideoCapture(self.rtsp_url)

        if not self._cap.isOpened():
            print(f"Failed to open RTSP stream: {self.rtsp_url}")
            return False

        # Set buffer size to minimize latency
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        return True

    def disconnect(self) -> None:
        """Disconnect from stream."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def get_frame(self) -> np.ndarray | None:
        """Capture single frame from stream.

        Returns:
            Frame as numpy array or None if failed
        """
        if self._cap is None or not self._cap.isOpened():
            if not self.connect():
                return None

        ret, frame = self._cap.read()
        if not ret:
            print("Failed to read frame")
            return None

        return frame

    def frames(self, max_frames: int | None = None) -> Generator[np.ndarray, None, None]:
        """Generator yielding frames from stream.

        Args:
            max_frames: Maximum number of frames to yield (None for infinite)

        Yields:
            Video frames as numpy arrays
        """
        count = 0
        while max_frames is None or count < max_frames:
            frame = self.get_frame()
            if frame is None:
                # Try to reconnect
                time.sleep(self.reconnect_delay)
                self.disconnect()
                if not self.connect():
                    break
                continue

            yield frame
            count += 1

    def add_frame_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """Add callback function to be called on each frame.

        Args:
            callback: Function that receives frame array
        """
        self._frame_callbacks.append(callback)

    def start_continuous_capture(self) -> None:
        """Start continuous frame capture in background thread."""
        if self._running:
            return

        self._running = True
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()

    def stop_continuous_capture(self) -> None:
        """Stop continuous capture."""
        self._running = False
        if self._capture_thread is not None:
            self._capture_thread.join(timeout=5.0)
            self._capture_thread = None

    def _capture_loop(self) -> None:
        """Internal capture loop running in thread."""
        while self._running:
            frame = self.get_frame()
            if frame is None:
                time.sleep(self.reconnect_delay)
                self.disconnect()
                self.connect()
                continue

            with self._frame_lock:
                self._last_frame = frame

            for callback in self._frame_callbacks:
                try:
                    callback(frame)
                except Exception as e:
                    print(f"Frame callback error: {e}")

    def get_latest_frame(self) -> np.ndarray | None:
        """Get most recent frame from continuous capture.

        Returns:
            Latest frame or None
        """
        with self._frame_lock:
            return self._last_frame.copy() if self._last_frame is not None else None

    def save_snapshot(self, output_path: str | Path | None = None) -> Path | None:
        """Save current frame as image.

        Args:
            output_path: Output file path (auto-generated if None)

        Returns:
            Path to saved image or None if failed
        """
        frame = self.get_frame()
        if frame is None:
            return None

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"snapshot_{timestamp}.jpg")
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), frame)
        return output_path

    def record_clip(
        self,
        output_path: str | Path,
        duration_seconds: float,
        fps: float = 15.0,
    ) -> bool:
        """Record video clip to file.

        Args:
            output_path: Output video file path
            duration_seconds: Recording duration
            fps: Frames per second

        Returns:
            True if recording successful
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get first frame to determine dimensions
        frame = self.get_frame()
        if frame is None:
            return False

        height, width = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        if not writer.isOpened():
            print(f"Failed to create video writer for {output_path}")
            return False

        try:
            frame_interval = 1.0 / fps
            total_frames = int(duration_seconds * fps)

            for i in range(total_frames):
                start_time = time.time()

                frame = self.get_frame()
                if frame is not None:
                    writer.write(frame)

                # Maintain frame rate
                elapsed = time.time() - start_time
                if elapsed < frame_interval:
                    time.sleep(frame_interval - elapsed)

            return True
        finally:
            writer.release()

    def get_stream_info(self) -> dict:
        """Get stream properties.

        Returns:
            Dictionary with stream properties
        """
        if self._cap is None or not self._cap.isOpened():
            if not self.connect():
                return {}

        return {
            "width": int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": self._cap.get(cv2.CAP_PROP_FPS),
            "backend": self._cap.getBackendName(),
        }

    def __enter__(self) -> "StreamCapture":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop_continuous_capture()
        self.disconnect()
