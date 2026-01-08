"""High-level UI automation for Tapo app."""

import time
from pathlib import Path
from dataclasses import dataclass
from typing import Callable

from .controller import AndroidController
from .screen import ScreenCapture


@dataclass
class UIElement:
    """Represents a UI element on screen."""
    name: str
    x: int
    y: int
    width: int = 0
    height: int = 0

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def center_y(self) -> int:
        return self.y + self.height // 2


class UIAutomation:
    """High-level UI automation for Tapo camera app."""

    # Common Tapo app UI element positions (adjust for your device)
    # These are relative positions that may need calibration
    UI_ELEMENTS = {
        "camera_preview": UIElement("camera_preview", 0, 200, 1080, 720),
        "ptz_up": UIElement("ptz_up", 540, 1000),
        "ptz_down": UIElement("ptz_down", 540, 1200),
        "ptz_left": UIElement("ptz_left", 440, 1100),
        "ptz_right": UIElement("ptz_right", 640, 1100),
        "record_button": UIElement("record_button", 200, 1400),
        "screenshot_button": UIElement("screenshot_button", 400, 1400),
        "settings_button": UIElement("settings_button", 900, 100),
        "playback_button": UIElement("playback_button", 600, 1400),
        "more_button": UIElement("more_button", 800, 1400),
    }

    def __init__(
        self,
        controller: AndroidController | None = None,
        screen: ScreenCapture | None = None,
    ):
        """Initialize UI automation.

        Args:
            controller: AndroidController instance (created if None)
            screen: ScreenCapture instance (created if None)
        """
        self.controller = controller or AndroidController()
        self.screen = screen or ScreenCapture(self.controller)
        self._connected = False

    def connect(self) -> bool:
        """Connect to device.

        Returns:
            True if connected successfully
        """
        self._connected = self.controller.connect()
        return self._connected

    def ensure_connected(self) -> None:
        """Ensure device is connected."""
        if not self._connected:
            if not self.connect():
                raise RuntimeError("Failed to connect to device")

    def calibrate_ui(self) -> dict:
        """Capture screen and help calibrate UI element positions.

        Returns:
            Current screen info for calibration
        """
        self.ensure_connected()

        img = self.screen.capture()
        width, height = img.size

        return {
            "screen_width": width,
            "screen_height": height,
            "current_elements": self.UI_ELEMENTS,
            "instructions": "Adjust UI_ELEMENTS coordinates based on your device",
        }

    def open_tapo_app(self) -> bool:
        """Open Tapo app and wait for it to load.

        Returns:
            True if app opened successfully
        """
        self.ensure_connected()

        self.controller.wake_screen()
        self.controller.launch_tapo()
        time.sleep(3)

        # Wait for app to be visible
        return self.screen.wait_for_text("Tapo", timeout_seconds=10)

    def close_tapo_app(self) -> None:
        """Close Tapo app."""
        self.ensure_connected()
        self.controller.stop_tapo()

    def tap_element(self, element_name: str) -> bool:
        """Tap on a named UI element.

        Args:
            element_name: Name from UI_ELEMENTS

        Returns:
            True if element exists and was tapped
        """
        self.ensure_connected()

        if element_name not in self.UI_ELEMENTS:
            print(f"Unknown element: {element_name}")
            return False

        elem = self.UI_ELEMENTS[element_name]
        self.controller.tap(elem.center_x, elem.center_y)
        return True

    def select_camera(self, camera_name: str) -> bool:
        """Select a camera from the device list.

        Args:
            camera_name: Camera name to find and tap

        Returns:
            True if camera found and selected
        """
        self.ensure_connected()

        # First try to find by text
        if self.screen.tap_text(camera_name):
            time.sleep(2)
            return True

        # Scroll down and try again
        w, h = self.screen.screen_size
        self.controller.swipe(w // 2, h * 2 // 3, w // 2, h // 3, 500)
        time.sleep(1)

        return self.screen.tap_text(camera_name)

    def move_camera(self, direction: str, duration_ms: int = 300) -> None:
        """Move camera using PTZ controls.

        Args:
            direction: 'up', 'down', 'left', 'right'
            duration_ms: Hold duration for movement
        """
        self.ensure_connected()

        direction_map = {
            "up": "ptz_up",
            "down": "ptz_down",
            "left": "ptz_left",
            "right": "ptz_right",
        }

        if direction not in direction_map:
            print(f"Invalid direction: {direction}")
            return

        elem = self.UI_ELEMENTS[direction_map[direction]]
        self.controller.long_press(elem.center_x, elem.center_y, duration_ms)

    def take_screenshot_in_app(self) -> bool:
        """Trigger screenshot in Tapo app.

        Returns:
            True if screenshot button tapped
        """
        return self.tap_element("screenshot_button")

    def start_recording_in_app(self) -> bool:
        """Start video recording in Tapo app.

        Returns:
            True if record button tapped
        """
        return self.tap_element("record_button")

    def stop_recording_in_app(self) -> bool:
        """Stop video recording in Tapo app.

        Returns:
            True if record button tapped (toggle)
        """
        return self.tap_element("record_button")

    def open_playback(self) -> bool:
        """Open playback/recordings view.

        Returns:
            True if playback button tapped
        """
        return self.tap_element("playback_button")

    def open_settings(self) -> bool:
        """Open camera settings.

        Returns:
            True if settings opened
        """
        return self.tap_element("settings_button")

    def scroll_down(self) -> None:
        """Scroll down on current screen."""
        self.ensure_connected()
        w, h = self.screen.screen_size
        self.controller.swipe(w // 2, h * 2 // 3, w // 2, h // 3, 300)

    def scroll_up(self) -> None:
        """Scroll up on current screen."""
        self.ensure_connected()
        w, h = self.screen.screen_size
        self.controller.swipe(w // 2, h // 3, w // 2, h * 2 // 3, 300)

    def go_back(self) -> None:
        """Press back button."""
        self.ensure_connected()
        self.controller.back()

    def go_home(self) -> None:
        """Press home button."""
        self.ensure_connected()
        self.controller.home()

    def get_visible_text(self) -> str:
        """Get all visible text on screen.

        Returns:
            Extracted text
        """
        self.ensure_connected()
        return self.screen.get_all_text()

    def wait_and_tap(
        self,
        text: str,
        timeout_seconds: float = 10.0,
    ) -> bool:
        """Wait for text to appear and tap it.

        Args:
            text: Text to find and tap
            timeout_seconds: Maximum wait time

        Returns:
            True if text found and tapped
        """
        self.ensure_connected()

        if self.screen.wait_for_text(text, timeout_seconds):
            time.sleep(0.5)
            return self.screen.tap_text(text)
        return False

    def execute_sequence(
        self,
        steps: list[dict],
        delay_between: float = 1.0,
    ) -> list[bool]:
        """Execute a sequence of UI actions.

        Args:
            steps: List of action dictionaries with 'action' and params
            delay_between: Delay between steps in seconds

        Returns:
            List of success/failure for each step

        Example steps:
            [
                {"action": "tap_text", "text": "Camera 1"},
                {"action": "move_camera", "direction": "up", "duration_ms": 500},
                {"action": "screenshot"},
            ]
        """
        self.ensure_connected()
        results = []

        for step in steps:
            action = step.get("action")
            success = False

            try:
                if action == "tap_text":
                    success = self.screen.tap_text(step["text"])
                elif action == "tap_element":
                    success = self.tap_element(step["element"])
                elif action == "move_camera":
                    self.move_camera(
                        step["direction"],
                        step.get("duration_ms", 300),
                    )
                    success = True
                elif action == "screenshot":
                    success = self.take_screenshot_in_app()
                elif action == "wait_text":
                    success = self.screen.wait_for_text(
                        step["text"],
                        step.get("timeout", 10.0),
                    )
                elif action == "back":
                    self.go_back()
                    success = True
                elif action == "scroll_down":
                    self.scroll_down()
                    success = True
                elif action == "scroll_up":
                    self.scroll_up()
                    success = True
                elif action == "sleep":
                    time.sleep(step.get("seconds", 1.0))
                    success = True
                else:
                    print(f"Unknown action: {action}")

            except Exception as e:
                print(f"Step failed: {step} - {e}")

            results.append(success)
            time.sleep(delay_between)

        return results

    def capture_camera_stream_region(self) -> "Image.Image":
        """Capture just the camera preview region.

        Returns:
            PIL Image of camera preview area
        """
        self.ensure_connected()
        elem = self.UI_ELEMENTS["camera_preview"]
        return self.screen.capture_region(
            elem.x,
            elem.y,
            elem.width,
            elem.height,
        )

    def get_current_state(self) -> dict:
        """Get current UI state information.

        Returns:
            Dictionary with current state
        """
        self.ensure_connected()

        return {
            "device_info": self.controller.get_device_info(),
            "tapo_running": self.controller.is_tapo_running(),
            "current_activity": self.controller.get_current_activity(),
            "screen_text_sample": self.get_visible_text()[:500],
        }
