"""Core Android device controller using ADB."""

import subprocess
import time
from pathlib import Path
from typing import Callable

try:
    from ppadb.client import Client as AdbClient
    PPADB_AVAILABLE = True
except ImportError:
    PPADB_AVAILABLE = False


class AndroidController:
    """Control Android device via ADB for Tapo app automation."""

    TAPO_PACKAGE = "com.tplink.iot"

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5037,
        device_serial: str | None = None,
    ):
        """Initialize Android controller.

        Args:
            host: ADB server host
            port: ADB server port
            device_serial: Specific device serial (None for first device)
        """
        self.host = host
        self.port = port
        self.device_serial = device_serial
        self._client = None
        self._device = None

    def connect(self) -> bool:
        """Connect to ADB and device.

        Returns:
            True if connection successful
        """
        if PPADB_AVAILABLE:
            return self._connect_ppadb()
        return self._connect_subprocess()

    def _connect_ppadb(self) -> bool:
        """Connect using pure-python-adb."""
        try:
            self._client = AdbClient(host=self.host, port=self.port)
            devices = self._client.devices()

            if not devices:
                print("No devices connected")
                return False

            if self.device_serial:
                self._device = self._client.device(self.device_serial)
            else:
                self._device = devices[0]

            print(f"Connected to device: {self._device.serial}")
            return True
        except Exception as e:
            print(f"Failed to connect via ppadb: {e}")
            return False

    def _connect_subprocess(self) -> bool:
        """Connect using subprocess ADB commands."""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            lines = result.stdout.strip().split("\n")[1:]
            devices = [l.split()[0] for l in lines if l.strip() and "device" in l]

            if not devices:
                print("No devices connected")
                return False

            self.device_serial = self.device_serial or devices[0]
            print(f"Connected to device: {self.device_serial}")
            return True
        except FileNotFoundError:
            print("ADB not found. Install android-tools package.")
            return False
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def shell(self, command: str) -> str:
        """Execute shell command on device.

        Args:
            command: Shell command to execute

        Returns:
            Command output
        """
        if self._device and PPADB_AVAILABLE:
            return self._device.shell(command)

        result = subprocess.run(
            ["adb", "-s", self.device_serial, "shell", command],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout

    def tap(self, x: int, y: int) -> None:
        """Simulate screen tap at coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.shell(f"input tap {x} {y}")

    def swipe(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration_ms: int = 300,
    ) -> None:
        """Simulate swipe gesture.

        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            duration_ms: Swipe duration in milliseconds
        """
        self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Simulate long press.

        Args:
            x: X coordinate
            y: Y coordinate
            duration_ms: Press duration
        """
        self.shell(f"input swipe {x} {y} {x} {y} {duration_ms}")

    def key_event(self, keycode: int | str) -> None:
        """Send key event.

        Args:
            keycode: Android keycode (number or name like KEYCODE_HOME)
        """
        self.shell(f"input keyevent {keycode}")

    def text(self, text: str) -> None:
        """Type text.

        Args:
            text: Text to type (spaces will be encoded)
        """
        # Escape special characters for shell
        escaped = text.replace(" ", "%s").replace("'", "\\'")
        self.shell(f"input text '{escaped}'")

    def back(self) -> None:
        """Press back button."""
        self.key_event(4)  # KEYCODE_BACK

    def home(self) -> None:
        """Press home button."""
        self.key_event(3)  # KEYCODE_HOME

    def enter(self) -> None:
        """Press enter key."""
        self.key_event(66)  # KEYCODE_ENTER

    def volume_up(self) -> None:
        """Press volume up."""
        self.key_event(24)  # KEYCODE_VOLUME_UP

    def volume_down(self) -> None:
        """Press volume down."""
        self.key_event(25)  # KEYCODE_VOLUME_DOWN

    def power(self) -> None:
        """Press power button."""
        self.key_event(26)  # KEYCODE_POWER

    def screenshot(self, local_path: str | Path) -> Path:
        """Take screenshot and pull to local machine.

        Args:
            local_path: Local path to save screenshot

        Returns:
            Path to saved screenshot
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        remote_path = "/sdcard/screenshot_temp.png"

        # Take screenshot
        self.shell(f"screencap -p {remote_path}")

        # Pull to local
        if self._device and PPADB_AVAILABLE:
            self._device.pull(remote_path, str(local_path))
        else:
            subprocess.run(
                ["adb", "-s", self.device_serial, "pull", remote_path, str(local_path)],
                capture_output=True,
                timeout=30,
            )

        # Clean up remote file
        self.shell(f"rm {remote_path}")

        return local_path

    def screen_record(
        self,
        local_path: str | Path,
        duration_seconds: int = 10,
        bit_rate: int = 4000000,
    ) -> Path:
        """Record screen video.

        Args:
            local_path: Local path to save video
            duration_seconds: Recording duration (max 180)
            bit_rate: Video bitrate

        Returns:
            Path to saved video
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        remote_path = "/sdcard/screenrecord_temp.mp4"
        duration_seconds = min(duration_seconds, 180)

        # Start recording (blocks)
        self.shell(
            f"screenrecord --time-limit {duration_seconds} --bit-rate {bit_rate} {remote_path}"
        )

        # Pull to local
        if self._device and PPADB_AVAILABLE:
            self._device.pull(remote_path, str(local_path))
        else:
            subprocess.run(
                ["adb", "-s", self.device_serial, "pull", remote_path, str(local_path)],
                capture_output=True,
                timeout=duration_seconds + 30,
            )

        # Clean up
        self.shell(f"rm {remote_path}")

        return local_path

    def get_screen_size(self) -> tuple[int, int]:
        """Get device screen resolution.

        Returns:
            Tuple of (width, height)
        """
        output = self.shell("wm size")
        # Output: "Physical size: 1080x2340"
        for line in output.split("\n"):
            if "size:" in line.lower():
                size_str = line.split(":")[-1].strip()
                w, h = size_str.split("x")
                return int(w), int(h)
        return 1080, 1920  # Default fallback

    def is_screen_on(self) -> bool:
        """Check if screen is on.

        Returns:
            True if screen is on
        """
        output = self.shell("dumpsys power | grep 'Display Power'")
        return "ON" in output.upper()

    def wake_screen(self) -> None:
        """Wake up screen if off."""
        if not self.is_screen_on():
            self.power()
            time.sleep(0.5)

    def get_current_activity(self) -> str:
        """Get current foreground activity.

        Returns:
            Activity name string
        """
        output = self.shell("dumpsys activity activities | grep mCurrentFocus")
        return output.strip()

    def launch_app(self, package: str, activity: str | None = None) -> None:
        """Launch an app.

        Args:
            package: Package name
            activity: Optional activity name
        """
        if activity:
            self.shell(f"am start -n {package}/{activity}")
        else:
            self.shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")

    def stop_app(self, package: str) -> None:
        """Force stop an app.

        Args:
            package: Package name
        """
        self.shell(f"am force-stop {package}")

    def is_app_running(self, package: str) -> bool:
        """Check if app is currently running.

        Args:
            package: Package name

        Returns:
            True if app is running
        """
        output = self.shell(f"pidof {package}")
        return bool(output.strip())

    def launch_tapo(self) -> None:
        """Launch Tapo app."""
        self.launch_app(self.TAPO_PACKAGE)
        time.sleep(3)  # Wait for app to load

    def stop_tapo(self) -> None:
        """Stop Tapo app."""
        self.stop_app(self.TAPO_PACKAGE)

    def is_tapo_running(self) -> bool:
        """Check if Tapo app is running."""
        return self.is_app_running(self.TAPO_PACKAGE)

    def get_device_info(self) -> dict:
        """Get device information.

        Returns:
            Dictionary with device properties
        """
        return {
            "serial": self.device_serial,
            "model": self.shell("getprop ro.product.model").strip(),
            "android_version": self.shell("getprop ro.build.version.release").strip(),
            "sdk_version": self.shell("getprop ro.build.version.sdk").strip(),
            "screen_size": self.get_screen_size(),
            "screen_on": self.is_screen_on(),
        }
