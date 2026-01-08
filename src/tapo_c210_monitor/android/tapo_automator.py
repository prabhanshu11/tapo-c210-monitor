"""Tapo app automation using LLM vision for UI control."""

import time
from pathlib import Path
from dataclasses import dataclass

from .controller import AndroidController
from .intelligent_screen import IntelligentScreen


@dataclass
class TapoCredentials:
    """Tapo account credentials."""
    email: str
    password: str


@dataclass
class CameraConfig:
    """Camera configuration from Tapo app."""
    device_name: str
    ip_address: str
    rtsp_username: str | None = None
    rtsp_password: str | None = None
    stream_url: str | None = None


class TapoAutomator:
    """Automate Tapo app to set up and control camera.

    This class uses LLM vision to navigate the Tapo app UI
    without relying on fixed coordinates or templates.
    """

    TAPO_PACKAGE = "com.tplink.iot"

    def __init__(
        self,
        device_id: str | None = None,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
    ):
        """Initialize Tapo automator.

        Args:
            device_id: ADB device ID (None for default)
            api_key: OpenRouter API key
            model: LLM model for vision
        """
        self.controller = AndroidController(device_id)
        self.screen = IntelligentScreen(self.controller, api_key, model)

    def is_app_installed(self) -> bool:
        """Check if Tapo app is installed."""
        return self.controller.is_app_installed(self.TAPO_PACKAGE)

    def launch_app(self) -> bool:
        """Launch Tapo app."""
        self.controller.launch_app(self.TAPO_PACKAGE)
        time.sleep(3)  # Wait for app to start
        return self.controller.is_app_running(self.TAPO_PACKAGE)

    def close_app(self):
        """Close Tapo app."""
        self.controller.stop_app(self.TAPO_PACKAGE)

    def login(self, credentials: TapoCredentials) -> bool:
        """Log into Tapo account.

        Args:
            credentials: Tapo account credentials

        Returns:
            True if login successful
        """
        if not self.launch_app():
            return False

        # Wait for login screen
        if not self.screen.wait_for_element("email or login field", timeout_seconds=10):
            # Might already be logged in
            if self.screen.find_element("home screen or device list"):
                return True
            return False

        # Enter email
        if not self.screen.tap_element("email input field"):
            return False
        time.sleep(0.5)
        self.controller.text(credentials.email)

        # Enter password
        if not self.screen.tap_element("password input field"):
            return False
        time.sleep(0.5)
        self.controller.text(credentials.password)

        # Tap login button
        if not self.screen.tap_and_wait("login button", "home screen", timeout=15):
            return False

        return True

    def add_device(self) -> bool:
        """Start the add device flow.

        Returns:
            True if device addition started
        """
        # Look for add device button (usually + icon)
        return self.screen.tap_and_wait(
            "add device button or plus icon",
            "device category or camera selection",
            timeout=10,
        )

    def select_camera_type(self, camera_type: str = "C210") -> bool:
        """Select camera type in device setup.

        Args:
            camera_type: Camera model (e.g., "C210")

        Returns:
            True if camera type selected
        """
        # Navigate to cameras category
        if not self.screen.tap_element("cameras category"):
            return False
        time.sleep(1)

        # Find and select the specific camera
        return self.screen.tap_element(f"{camera_type} camera option")

    def setup_camera_wifi(self, ssid: str, wifi_password: str) -> bool:
        """Configure camera WiFi during setup.

        Args:
            ssid: WiFi network name
            wifi_password: WiFi password

        Returns:
            True if WiFi configured
        """
        # Wait for WiFi setup screen
        if not self.screen.wait_for_element("WiFi setup or network selection", timeout_seconds=30):
            return False

        # Select network
        if not self.screen.tap_element(f"network {ssid}"):
            # Might need to enter manually
            if not self.screen.tap_element("other network or manual entry"):
                return False
            time.sleep(0.5)
            self.controller.text(ssid)

        # Enter password
        time.sleep(1)
        if self.screen.tap_element("password field"):
            time.sleep(0.3)
            self.controller.text(wifi_password)

        # Confirm
        return self.screen.tap_element("next or connect button")

    def wait_for_device_connection(self, timeout: float = 120) -> bool:
        """Wait for device to connect during setup.

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if device connected successfully
        """
        start = time.time()
        while time.time() - start < timeout:
            # Check for success indicators
            if self.screen.find_element("device added successfully"):
                return True
            if self.screen.find_element("setup complete"):
                return True
            if self.screen.find_element("camera preview or live feed"):
                return True

            # Check for failure indicators
            if self.screen.find_element("connection failed"):
                return False

            time.sleep(2)

        return False

    def get_device_ip(self, device_name: str | None = None) -> str | None:
        """Get camera IP address from app.

        Args:
            device_name: Specific device name (optional)

        Returns:
            IP address if found
        """
        # Navigate to device settings
        if device_name:
            if not self.screen.tap_element(f"device {device_name}"):
                return None
        else:
            # Tap on first/only camera
            if not self.screen.tap_element("camera device or first device"):
                return None

        time.sleep(1)

        # Go to device settings/info
        if not self.screen.tap_element("settings or gear icon"):
            return None
        time.sleep(1)

        # Look for device info section
        if not self.screen.tap_element("device info or about device"):
            return None
        time.sleep(1)

        # Analyze screen for IP address
        result = self.screen.analyze("Find the IP address displayed on this screen")
        for element in result.elements:
            if "." in element.name and element.name.count(".") == 3:
                # Looks like an IP address
                return element.name

        return None

    def enable_rtsp(self) -> dict | None:
        """Enable RTSP streaming and get credentials.

        Returns:
            Dict with rtsp_username, rtsp_password, stream_url if successful
        """
        # Navigate to advanced settings
        if not self.screen.tap_element("advanced settings"):
            return None
        time.sleep(1)

        # Find RTSP or streaming option
        if not self.screen.tap_element("RTSP stream or camera account"):
            return None
        time.sleep(1)

        # Enable if not already enabled
        self.screen.tap_element("enable toggle or switch")
        time.sleep(1)

        # Analyze screen for credentials
        result = self.screen.analyze("Find RTSP username, password, and stream URL on this screen")

        rtsp_info = {}
        for element in result.elements:
            name_lower = element.name.lower()
            if "username" in element.description.lower():
                rtsp_info["username"] = element.name
            elif "password" in element.description.lower():
                rtsp_info["password"] = element.name
            elif "rtsp://" in element.name:
                rtsp_info["stream_url"] = element.name

        return rtsp_info if rtsp_info else None

    def pan_camera(self, direction: str) -> bool:
        """Pan camera in a direction.

        Args:
            direction: One of "left", "right", "up", "down"

        Returns:
            True if pan command sent
        """
        # Make sure we're on the live view
        if not self.screen.find_element("camera live view or video feed"):
            self.screen.tap_element("camera device or first device")
            time.sleep(2)

        # Find PTZ control or swipe on the video
        element = self.screen.find_element("PTZ control or direction pad")
        if element:
            # Use PTZ controls
            return self.screen.tap_element(f"{direction} arrow or {direction} button")
        else:
            # Swipe on the video feed
            width, height = self.controller.get_screen_size()
            center_x, center_y = width // 2, height // 3

            swipe_map = {
                "left": (center_x + 100, center_y, center_x - 100, center_y),
                "right": (center_x - 100, center_y, center_x + 100, center_y),
                "up": (center_x, center_y + 100, center_x, center_y - 100),
                "down": (center_x, center_y - 100, center_x, center_y + 100),
            }

            if direction in swipe_map:
                x1, y1, x2, y2 = swipe_map[direction]
                self.controller.swipe(x1, y1, x2, y2)
                return True

        return False

    def get_current_screen_description(self) -> str:
        """Get description of current screen."""
        return self.screen.get_screen_description()

    def save_screenshot(self, path: str | Path) -> Path:
        """Save current screen to file."""
        return self.screen.save_screenshot(path)

    def go_back(self):
        """Press back button."""
        self.controller.key_event("KEYCODE_BACK")
        time.sleep(0.5)

    def go_home(self):
        """Go to device home screen."""
        self.controller.key_event("KEYCODE_HOME")
        time.sleep(0.5)

    def close(self):
        """Clean up resources."""
        self.screen.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
