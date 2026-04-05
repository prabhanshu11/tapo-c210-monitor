"""Night vision (IR LED) control for Tapo C210 camera via pytapo.

This module provides programmatic control of the camera's infrared LEDs,
allowing switching between day mode (color), night vision (IR/grayscale),
and automatic mode.

Requirements:
    - pytapo library
    - TP-Link cloud credentials (email + password)
    - Third-Party Compatibility enabled in Tapo app

Usage:
    from tapo_c210_monitor.night_vision import TapoNightVision, NightVisionMode

    nv = TapoNightVision("192.168.50.199", "admin", cloud_password)

    # Enable night vision (IR LEDs on)
    nv.set_mode(NightVisionMode.ON)

    # Enable day mode (IR LEDs off)
    nv.set_mode(NightVisionMode.OFF)

    # Auto mode (camera decides based on light level)
    nv.set_mode(NightVisionMode.AUTO)
"""

from enum import Enum
from typing import Optional
import subprocess


class NightVisionMode(Enum):
    """Night vision / IR LED mode."""
    OFF = "off"   # IR LEDs off - day mode (color vision)
    ON = "on"     # IR LEDs on - night vision (grayscale)
    AUTO = "auto" # Automatic - camera switches based on ambient light


class TapoNightVision:
    """Control night vision (IR LEDs) on Tapo C210 camera."""

    def __init__(self, host: str, user: str, password: str):
        """Initialize connection to camera.

        Args:
            host: Camera IP address
            user: Username (usually "admin")
            password: TP-Link cloud password (NOT camera account password)
        """
        self.host = host
        self.user = user
        self.password = password
        self._tapo = None

    def connect(self) -> bool:
        """Connect to camera via pytapo.

        Returns:
            True if connection successful
        """
        try:
            from pytapo import Tapo
            self._tapo = Tapo(self.host, self.user, self.password)
            # Test connection by getting basic info
            self._tapo.getBasicInfo()
            return True
        except Exception as e:
            print(f"[NightVision] Connection failed: {e}")
            return False

    def get_mode(self) -> Optional[NightVisionMode]:
        """Get current night vision mode.

        Returns:
            Current NightVisionMode or None if error
        """
        if self._tapo is None:
            if not self.connect():
                return None

        try:
            config = self._tapo.getDayNightModeConfig()
            inf_type = config.get('image', {}).get('common', {}).get('inf_type', 'unknown')
            return NightVisionMode(inf_type)
        except ValueError:
            return None
        except Exception as e:
            print(f"[NightVision] Error getting mode: {e}")
            return None

    def set_mode(self, mode: NightVisionMode) -> bool:
        """Set night vision mode.

        Args:
            mode: Desired NightVisionMode

        Returns:
            True if mode was set successfully
        """
        if self._tapo is None:
            if not self.connect():
                return False

        try:
            # pytapo's setDayNightMode uses __setImageCommon which doesn't work
            # on C210. Use direct executeFunction instead.
            result = self._tapo.executeFunction(
                "setDayNightModeConfig",
                {"image": {"common": {"inf_type": mode.value}}}
            )
            return True
        except Exception as e:
            print(f"[NightVision] Error setting mode: {e}")
            return False

    def enable_night_vision(self) -> bool:
        """Enable night vision (turn IR LEDs on).

        Returns:
            True if successful
        """
        return self.set_mode(NightVisionMode.ON)

    def disable_night_vision(self) -> bool:
        """Disable night vision (turn IR LEDs off, color mode).

        Returns:
            True if successful
        """
        return self.set_mode(NightVisionMode.OFF)

    def set_auto_mode(self) -> bool:
        """Set automatic night vision mode.

        Returns:
            True if successful
        """
        return self.set_mode(NightVisionMode.AUTO)


def get_cloud_password() -> str:
    """Get Tapo cloud password from pass password manager.

    Returns:
        Password string
    """
    return subprocess.check_output(
        ["pass", "show", "tapo/cloud-password"]
    ).decode().strip()


# CLI interface
if __name__ == "__main__":
    import sys

    HOST = "192.168.50.199"
    USER = "admin"

    usage = """
Usage: python -m tapo_c210_monitor.night_vision <command>

Commands:
    status  - Show current night vision mode
    on      - Enable night vision (IR LEDs on)
    off     - Disable night vision (day mode)
    auto    - Set automatic mode
"""

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    command = sys.argv[1].lower()
    nv = TapoNightVision(HOST, USER, get_cloud_password())

    if command == "status":
        mode = nv.get_mode()
        if mode:
            print(f"Night vision mode: {mode.name} ({mode.value})")
        else:
            print("Failed to get mode")
            sys.exit(1)

    elif command == "on":
        if nv.enable_night_vision():
            print("Night vision enabled (IR LEDs on)")
        else:
            print("Failed to enable night vision")
            sys.exit(1)

    elif command == "off":
        if nv.disable_night_vision():
            print("Night vision disabled (day mode)")
        else:
            print("Failed to disable night vision")
            sys.exit(1)

    elif command == "auto":
        if nv.set_auto_mode():
            print("Night vision set to auto")
        else:
            print("Failed to set auto mode")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        print(usage)
        sys.exit(1)
