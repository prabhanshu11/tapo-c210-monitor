"""Tapo Camera Controls via Android UI Automation.

This module provides high-level control of the Tapo C210 camera through
the Android app UI, using coordinates discovered via multi-agent exploration.
"""

import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from .controller import AndroidController


class PanDirection(Enum):
    """Camera pan/tilt directions."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class UICoordinates:
    """UI element tap coordinates for 320x640 screen resolution.

    These coordinates were discovered via multi-agent UI exploration.
    See: ui-exploration/screens/ for full documentation.
    """
    # Navigation
    HOME_CAMERA_CARD = (85, 220)  # Tap camera on home screen
    BACK_BUTTON = (24, 57)

    # Camera Live View controls
    TAKE_PHOTO = (50, 302)
    RECORD_VIDEO = (123, 302)
    MIC_VOLUME = (197, 302)
    VOICE_CALL = (270, 302)

    # Control panel row 1
    TALK = (64, 391)
    PAN_TILT = (160, 391)
    DETECTION_ALARM = (256, 391)

    # Control panel row 2
    PRIVACY_MODE = (64, 474)
    TAPO_CARE = (160, 474)

    # Video display controls
    MULTI_VIEW = (68, 244)
    VIDEO_MODE = (160, 244)
    FULLSCREEN = (252, 244)

    # Pan/Tilt directional buttons (when PTZ panel is open)
    PAN_UP = (160, 541)
    PAN_DOWN = (160, 625)
    PAN_LEFT = (108, 592)
    PAN_RIGHT = (208, 592)
    PTZ_CLOSE = (24, 381)
    PTZ_SETTINGS = (296, 381)

    # Storage & playback
    PLAYBACK_DOWNLOAD = (160, 577)

    # Bottom navigation (home screen)
    TAB_CAMERAS = (32, 615)
    TAB_VACUUMS = (96, 615)
    TAB_SMART = (160, 615)
    TAB_ME = (288, 615)

    # Settings (from camera live)
    DEVICE_SETTINGS = (296, 57)


class CameraControls:
    """High-level camera control interface.

    Usage:
        ctrl = CameraControls()
        ctrl.connect()
        ctrl.open_camera_live()
        ctrl.take_photo()
        ctrl.pan(PanDirection.LEFT, duration=2.0)
        ctrl.start_recording()
        time.sleep(10)
        ctrl.stop_recording()
    """

    CAMERA_LIVE_ACTIVITY = "com.tplink.iot/.view.ipcamerav3.play.VideoPlayV3Activity"
    HOME_ACTIVITY = "com.tplink.iot/.view.main.TapoMainActivity"

    def __init__(self, device_serial: Optional[str] = None):
        """Initialize camera controls.

        Args:
            device_serial: Specific emulator/device serial (e.g., 'emulator-5554')
        """
        self.controller = AndroidController(device_serial=device_serial)
        self.coords = UICoordinates()
        self._is_recording = False
        self._ptz_panel_open = False

    def connect(self) -> bool:
        """Connect to device."""
        return self.controller.connect()

    def _tap(self, coords: tuple[int, int], delay: float = 0.5) -> None:
        """Tap at coordinates with delay."""
        self.controller.tap(coords[0], coords[1])
        time.sleep(delay)

    def _is_on_camera_live(self) -> bool:
        """Check if we're on the camera live view screen."""
        activity = self.controller.get_current_activity()
        return "VideoPlayV3Activity" in activity

    def _is_on_home(self) -> bool:
        """Check if we're on the home screen."""
        activity = self.controller.get_current_activity()
        return "TapoMainActivity" in activity

    def _ensure_camera_live(self) -> bool:
        """Ensure we're on the camera live view screen.

        Returns:
            True if now on camera live, False if failed
        """
        if self._is_on_camera_live():
            return True

        # Try to navigate from home
        if self._is_on_home():
            self._tap(self.coords.HOME_CAMERA_CARD, delay=3.0)
            return self._is_on_camera_live()

        # Launch Tapo app and try again
        self.controller.launch_tapo()
        time.sleep(3)
        self._tap(self.coords.HOME_CAMERA_CARD, delay=3.0)
        return self._is_on_camera_live()

    def open_camera_live(self) -> bool:
        """Open the camera live view.

        Returns:
            True if successful
        """
        return self._ensure_camera_live()

    def go_back(self) -> None:
        """Press back button."""
        self._tap(self.coords.BACK_BUTTON)

    def go_home(self) -> None:
        """Return to app home screen."""
        if self._ptz_panel_open:
            self.close_ptz_panel()
        self.controller.back()
        time.sleep(1)

    # === Photo & Recording Controls ===

    def take_photo(self) -> bool:
        """Take a photo with the camera.

        Photo is saved to camera's SD card.

        Returns:
            True if on camera live view (photo taken)
        """
        if not self._ensure_camera_live():
            return False

        self._tap(self.coords.TAKE_PHOTO)
        return True

    def start_recording(self) -> bool:
        """Start video recording to SD card.

        Returns:
            True if recording started
        """
        if not self._ensure_camera_live():
            return False

        if self._is_recording:
            return True  # Already recording

        self._tap(self.coords.RECORD_VIDEO)
        self._is_recording = True
        return True

    def stop_recording(self) -> bool:
        """Stop video recording.

        Returns:
            True if recording stopped
        """
        if not self._is_recording:
            return True  # Not recording

        self._tap(self.coords.RECORD_VIDEO)
        self._is_recording = False
        return True

    def is_recording(self) -> bool:
        """Check if currently recording.

        Note: This is based on internal state. For actual UI state,
        would need to check UI dump for recording indicator.
        """
        return self._is_recording

    # === Pan/Tilt Controls ===

    def open_ptz_panel(self) -> bool:
        """Open the Pan/Tilt control panel.

        Returns:
            True if panel opened
        """
        if not self._ensure_camera_live():
            return False

        if self._ptz_panel_open:
            return True

        self._tap(self.coords.PAN_TILT, delay=0.5)
        self._ptz_panel_open = True
        return True

    def close_ptz_panel(self) -> None:
        """Close the PTZ control panel."""
        if self._ptz_panel_open:
            self._tap(self.coords.PTZ_CLOSE)
            self._ptz_panel_open = False

    def pan(self, direction: PanDirection, duration: float = 0.5) -> bool:
        """Pan/tilt the camera in a direction.

        Args:
            direction: Direction to pan (UP, DOWN, LEFT, RIGHT)
            duration: How long to hold the direction (seconds).
                      Use longer duration for more movement.

        Returns:
            True if pan executed
        """
        if not self.open_ptz_panel():
            return False

        # Get coordinates for direction
        coords_map = {
            PanDirection.UP: self.coords.PAN_UP,
            PanDirection.DOWN: self.coords.PAN_DOWN,
            PanDirection.LEFT: self.coords.PAN_LEFT,
            PanDirection.RIGHT: self.coords.PAN_RIGHT,
        }
        coords = coords_map[direction]

        # Long press for continuous movement
        duration_ms = int(duration * 1000)
        self.controller.long_press(coords[0], coords[1], duration_ms)
        time.sleep(0.3)  # Brief pause after movement
        return True

    def pan_up(self, duration: float = 0.5) -> bool:
        """Pan camera up."""
        return self.pan(PanDirection.UP, duration)

    def pan_down(self, duration: float = 0.5) -> bool:
        """Pan camera down."""
        return self.pan(PanDirection.DOWN, duration)

    def pan_left(self, duration: float = 0.5) -> bool:
        """Pan camera left."""
        return self.pan(PanDirection.LEFT, duration)

    def pan_right(self, duration: float = 0.5) -> bool:
        """Pan camera right."""
        return self.pan(PanDirection.RIGHT, duration)

    # === View Controls ===

    def toggle_fullscreen(self) -> bool:
        """Toggle fullscreen mode for maximum resolution feed.

        Returns:
            True if toggle executed
        """
        if not self._ensure_camera_live():
            return False

        self._tap(self.coords.FULLSCREEN)
        return True

    def toggle_privacy_mode(self) -> bool:
        """Toggle camera privacy mode (turns feed on/off).

        Returns:
            True if toggle executed
        """
        if not self._ensure_camera_live():
            return False

        self._tap(self.coords.PRIVACY_MODE)
        return True

    def open_playback(self) -> bool:
        """Open playback & download section.

        Note: This may cause ANR on some emulators.
        Recommended: Use Me tab -> Playback instead.

        Returns:
            True if tap executed
        """
        if not self._ensure_camera_live():
            return False

        self._tap(self.coords.PLAYBACK_DOWNLOAD, delay=2.0)
        return True

    def open_device_settings(self) -> bool:
        """Open device settings.

        Returns:
            True if tap executed
        """
        if not self._ensure_camera_live():
            return False

        self._tap(self.coords.DEVICE_SETTINGS, delay=2.0)
        return True

    # === Utility Methods ===

    def get_ui_dump(self) -> str:
        """Get UI automator XML dump.

        Returns:
            UI hierarchy XML string
        """
        self.controller.shell("uiautomator dump /sdcard/ui.xml")
        return self.controller.shell("cat /sdcard/ui.xml")

    def take_screenshot(self, path: str | Path) -> Path:
        """Take screenshot of current screen.

        Args:
            path: Local path to save screenshot

        Returns:
            Path to saved screenshot
        """
        return self.controller.screenshot(path)

    def get_screen_rotation(self) -> int:
        """Get current screen rotation.

        Returns:
            Rotation value (0, 1, 2, 3)
        """
        output = self.controller.shell("settings get system user_rotation")
        try:
            return int(output.strip())
        except ValueError:
            return 0

    def set_landscape_mode(self) -> None:
        """Force landscape mode for maximum video resolution."""
        # Disable auto-rotate
        self.controller.shell("settings put system accelerometer_rotation 0")
        # Set to landscape (rotation 1 = 90 degrees)
        self.controller.shell("settings put system user_rotation 1")
        time.sleep(0.5)

    def set_portrait_mode(self) -> None:
        """Force portrait mode."""
        self.controller.shell("settings put system accelerometer_rotation 0")
        self.controller.shell("settings put system user_rotation 0")
        time.sleep(0.5)

    def enable_auto_rotate(self) -> None:
        """Enable auto-rotation."""
        self.controller.shell("settings put system accelerometer_rotation 1")


def quick_test():
    """Quick test of camera controls."""
    ctrl = CameraControls()
    if not ctrl.connect():
        print("Failed to connect to device")
        return

    print("Opening camera live view...")
    if not ctrl.open_camera_live():
        print("Failed to open camera live")
        return

    print("Camera live view opened!")
    print(f"Current activity: {ctrl.controller.get_current_activity()}")

    # Take a photo
    print("\nTaking photo...")
    ctrl.take_photo()
    print("Photo taken!")

    # Test pan controls
    print("\nOpening PTZ panel...")
    ctrl.open_ptz_panel()

    print("Panning left...")
    ctrl.pan_left(duration=1.0)

    print("Panning right...")
    ctrl.pan_right(duration=1.0)

    print("Closing PTZ panel...")
    ctrl.close_ptz_panel()

    print("\nTest complete!")


if __name__ == "__main__":
    quick_test()
