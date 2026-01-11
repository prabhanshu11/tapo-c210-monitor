"""Pan Control Experiment - Validate actuator → visual change detection pipeline.

This experiment tests the core concept for intelligent camera monitoring:
1. Capture baseline frame via RTSP
2. Execute PAN command via Android emulator
3. Capture post-PAN frame via RTSP
4. Compare frames to detect visual shift

If this works, the same pipeline applies to any actuator (e.g., robotic arm
turning a gas knob) where we detect visual state changes.
"""

import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..android.camera_controls import CameraControls, PanDirection
from ..discovery import discover_camera, get_rtsp_url


@dataclass
class ExperimentResult:
    """Results from a single pan control experiment run."""

    timestamp: str
    direction: str
    pan_duration: float
    baseline_frame: Path
    post_pan_frame: Path
    visual_shift_detected: bool
    shift_magnitude: float  # 0.0 to 1.0
    camera_ip: str
    notes: str = ""


class RTSPFrameCapture:
    """Capture frames from RTSP stream using ffmpeg."""

    def __init__(
        self,
        rtsp_url: str,
        output_dir: Path,
        transport: str = "tcp",
    ):
        self.rtsp_url = rtsp_url
        self.output_dir = Path(output_dir)
        self.transport = transport
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture_frame(self, filename: Optional[str] = None) -> Path:
        """Capture a single frame from RTSP stream.

        Args:
            filename: Optional filename, defaults to timestamp

        Returns:
            Path to captured frame
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"frame_{timestamp}.jpg"

        output_path = self.output_dir / filename

        cmd = [
            "ffmpeg",
            "-rtsp_transport", self.transport,
            "-i", self.rtsp_url,
            "-frames:v", "1",
            "-update", "1",
            "-y",  # Overwrite
            str(output_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=15,
        )

        if result.returncode != 0 or not output_path.exists():
            raise RuntimeError(f"Failed to capture frame: {result.stderr.decode()}")

        return output_path


class VisualShiftDetector:
    """Detect visual shifts between two frames.

    This is a placeholder for the visual change detection algorithm.
    The user will implement the core comparison logic.
    """

    def __init__(self, threshold: float = 0.05):
        """Initialize detector.

        Args:
            threshold: Minimum shift magnitude to consider as "detected"
        """
        self.threshold = threshold

    def compare_frames(
        self,
        frame_before: Path,
        frame_after: Path,
    ) -> tuple[bool, float]:
        """Compare two frames and detect visual shift.

        Args:
            frame_before: Path to baseline frame
            frame_after: Path to post-action frame

        Returns:
            Tuple of (shift_detected, magnitude)
            magnitude is 0.0 to 1.0 indicating how much the image changed
        """
        # TODO: User implements comparison algorithm here
        # Options:
        # 1. Simple histogram difference
        # 2. Structural similarity (SSIM)
        # 3. Feature-based matching (ORB/SIFT)
        # 4. Optical flow estimation

        shift_magnitude = self._calculate_shift(frame_before, frame_after)
        shift_detected = shift_magnitude > self.threshold

        return shift_detected, shift_magnitude

    def _calculate_shift(self, before: Path, after: Path) -> float:
        """Calculate visual shift magnitude between frames.

        Uses histogram comparison for speed. For more sophisticated
        detection (e.g., SSIM, feature matching), modify this method.

        Returns a value between 0.0 (identical) and 1.0 (completely different).
        """
        try:
            import cv2
            import numpy as np

            # Load images
            img1 = cv2.imread(str(before))
            img2 = cv2.imread(str(after))

            if img1 is None or img2 is None:
                raise ValueError("Failed to load images")

            # Convert to grayscale for simpler comparison
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            # Method 1: Histogram comparison (fast)
            hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])

            # Normalize histograms
            cv2.normalize(hist1, hist1)
            cv2.normalize(hist2, hist2)

            # Compare using correlation (1 = identical, -1 = inverse)
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

            # Convert to shift magnitude (0 = identical, 1 = different)
            shift_magnitude = 1.0 - max(0.0, correlation)

            return shift_magnitude

        except ImportError:
            print("WARNING: opencv-python not installed. Using basic comparison.")
            # Fallback: basic file size comparison (very rough)
            size1 = before.stat().st_size
            size2 = after.stat().st_size
            return abs(size1 - size2) / max(size1, size2)


class PanControlExperiment:
    """Orchestrate the pan control experiment.

    Usage:
        exp = PanControlExperiment()
        exp.setup()
        result = exp.run(PanDirection.LEFT, duration=1.0)
        print(f"Visual shift detected: {result.visual_shift_detected}")
    """

    def __init__(
        self,
        output_dir: str = "/tmp/pan_experiment",
        device_serial: Optional[str] = None,
        camera_username: str = "prabhanshu",
        camera_password: str = "iamapantar",
        subnet: str = "192.168.29",
        camera_ip: Optional[str] = None,
    ):
        self.output_dir = Path(output_dir)
        self.device_serial = device_serial
        self.camera_username = camera_username
        self.camera_password = camera_password
        self.subnet = subnet
        self._provided_camera_ip = camera_ip  # Skip discovery if provided

        self.camera_ip: Optional[str] = None
        self.rtsp_url: Optional[str] = None
        self.frame_capture: Optional[RTSPFrameCapture] = None
        self.camera_controls: Optional[CameraControls] = None
        self.shift_detector: Optional[VisualShiftDetector] = None

        self._setup_complete = False

    def setup(self) -> bool:
        """Initialize all experiment components.

        Returns:
            True if setup successful
        """
        print("Setting up Pan Control Experiment...")

        # 1. Discover or use provided camera IP
        if self._provided_camera_ip:
            print(f"Using provided camera IP: {self._provided_camera_ip}")
            self.camera_ip = self._provided_camera_ip
        else:
            print(f"Discovering camera on {self.subnet}.0/24...")
            self.camera_ip = discover_camera(subnet=self.subnet)
            if not self.camera_ip:
                print("ERROR: Camera not found on network")
                print("TIP: Use --camera-ip to specify IP directly")
                return False
            print(f"Found camera at {self.camera_ip}")

        # 2. Setup RTSP
        self.rtsp_url = get_rtsp_url(
            self.camera_ip,
            self.camera_username,
            self.camera_password,
        )
        self.frame_capture = RTSPFrameCapture(
            self.rtsp_url,
            self.output_dir / "frames",
        )
        print(f"RTSP configured: {self.rtsp_url}")

        # 3. Test RTSP connection
        print("Testing RTSP connection...")
        try:
            test_frame = self.frame_capture.capture_frame("test_connection.jpg")
            print(f"RTSP working - test frame: {test_frame}")
        except Exception as e:
            print(f"ERROR: RTSP capture failed: {e}")
            return False

        # 4. Connect to Android emulator
        print("Connecting to Android emulator...")
        self.camera_controls = CameraControls(device_serial=self.device_serial)
        if not self.camera_controls.connect():
            print("ERROR: Failed to connect to emulator")
            return False
        print("Emulator connected")

        # 5. Initialize shift detector
        self.shift_detector = VisualShiftDetector()

        self._setup_complete = True
        print("Setup complete!")
        return True

    def run(
        self,
        direction: PanDirection = PanDirection.LEFT,
        pan_duration: float = 1.0,
        settle_time: float = 0.5,
    ) -> ExperimentResult:
        """Run a single experiment iteration.

        Args:
            direction: Which way to pan the camera
            pan_duration: How long to hold the pan (seconds)
            settle_time: Wait time after pan before capturing (seconds)

        Returns:
            ExperimentResult with captured frames and analysis
        """
        if not self._setup_complete:
            raise RuntimeError("Call setup() first")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\n=== Running experiment: {direction.value} @ {timestamp} ===")

        # 1. Capture baseline frame
        print("Capturing baseline frame...")
        baseline_frame = self.frame_capture.capture_frame(
            f"baseline_{timestamp}.jpg"
        )
        print(f"  Saved: {baseline_frame}")

        # 2. Execute PAN command
        print(f"Executing PAN {direction.value} for {pan_duration}s...")
        self.camera_controls.pan(direction, duration=pan_duration)

        # 3. Wait for camera to settle
        print(f"Waiting {settle_time}s for camera to settle...")
        time.sleep(settle_time)

        # 4. Capture post-PAN frame
        print("Capturing post-PAN frame...")
        post_pan_frame = self.frame_capture.capture_frame(
            f"post_pan_{timestamp}.jpg"
        )
        print(f"  Saved: {post_pan_frame}")

        # 5. Compare frames
        print("Analyzing visual shift...")
        shift_detected, magnitude = self.shift_detector.compare_frames(
            baseline_frame,
            post_pan_frame,
        )

        result = ExperimentResult(
            timestamp=timestamp,
            direction=direction.value,
            pan_duration=pan_duration,
            baseline_frame=baseline_frame,
            post_pan_frame=post_pan_frame,
            visual_shift_detected=shift_detected,
            shift_magnitude=magnitude,
            camera_ip=self.camera_ip,
        )

        print(f"\n=== Result ===")
        print(f"  Shift detected: {shift_detected}")
        print(f"  Magnitude: {magnitude:.3f}")
        print(f"  Frames saved to: {self.output_dir / 'frames'}")

        return result

    def run_full_test(self) -> list[ExperimentResult]:
        """Run full test sequence in all four directions.

        Returns:
            List of results for each direction
        """
        results = []

        for direction in [
            PanDirection.LEFT,
            PanDirection.RIGHT,
            PanDirection.UP,
            PanDirection.DOWN,
        ]:
            result = self.run(direction)
            results.append(result)
            time.sleep(1)  # Brief pause between tests

        return results


def quick_test():
    """Quick test of the pan control experiment."""
    exp = PanControlExperiment()

    if not exp.setup():
        print("\nSetup failed. Check:")
        print("  1. Camera is powered on and on network")
        print("  2. Android emulator is running with Tapo app")
        print("  3. RTSP credentials are correct")
        return

    # Run single test
    result = exp.run(PanDirection.LEFT, pan_duration=1.0)

    print("\n" + "=" * 50)
    print("EXPERIMENT COMPLETE")
    print("=" * 50)
    print(f"Baseline: {result.baseline_frame}")
    print(f"Post-PAN: {result.post_pan_frame}")
    print(f"\nOpen both images to visually confirm the camera moved!")
    print(f"\nNext step: Implement _calculate_shift() in VisualShiftDetector")


if __name__ == "__main__":
    quick_test()
