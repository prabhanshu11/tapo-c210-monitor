"""Core TAPO C210 camera interface using pytapo."""

import os
from typing import Any
from pytapo import Tapo


class TapoCamera:
    """Wrapper class for TAPO C210 camera operations."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        cloud_password: str | None = None,
    ):
        """Initialize camera connection.

        Args:
            host: Camera IP address
            username: Camera account username (created in Tapo app)
            password: Camera account password
            cloud_password: Optional TP-Link cloud password for fallback auth
        """
        self.host = host
        self.username = username
        self.password = password
        self.cloud_password = cloud_password
        self._tapo: Tapo | None = None

    def connect(self) -> bool:
        """Establish connection to the camera.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._tapo = Tapo(self.host, self.username, self.password)
            # Test connection by getting basic info
            self._tapo.getBasicInfo()
            return True
        except Exception as e:
            # Try fallback authentication with cloud password
            if self.cloud_password:
                try:
                    self._tapo = Tapo(self.host, "admin", self.cloud_password)
                    self._tapo.getBasicInfo()
                    return True
                except Exception:
                    pass
            print(f"Failed to connect to camera: {e}")
            return False

    @property
    def tapo(self) -> Tapo:
        """Get the underlying Tapo instance."""
        if self._tapo is None:
            raise RuntimeError("Camera not connected. Call connect() first.")
        return self._tapo

    def get_basic_info(self) -> dict[str, Any]:
        """Get basic camera information."""
        return self.tapo.getBasicInfo()

    def get_time(self) -> dict[str, Any]:
        """Get camera time settings."""
        return self.tapo.getTime()

    def get_led_status(self) -> bool:
        """Get LED indicator status."""
        return self.tapo.getLED()

    def set_led(self, enabled: bool) -> None:
        """Set LED indicator on/off."""
        self.tapo.setLED(enabled)

    def get_privacy_mode(self) -> bool:
        """Get privacy mode status (lens cover)."""
        return self.tapo.getPrivacyMode()

    def set_privacy_mode(self, enabled: bool) -> None:
        """Enable/disable privacy mode."""
        self.tapo.setPrivacyMode(enabled)

    def get_motion_detection(self) -> dict[str, Any]:
        """Get motion detection settings."""
        return self.tapo.getMotionDetection()

    def set_motion_detection(self, enabled: bool, sensitivity: str = "medium") -> None:
        """Configure motion detection.

        Args:
            enabled: Enable/disable motion detection
            sensitivity: 'low', 'medium', or 'high'
        """
        self.tapo.setMotionDetection(enabled, sensitivity)

    def get_alarm_status(self) -> dict[str, Any]:
        """Get alarm configuration."""
        return self.tapo.getAlarm()

    def set_alarm(self, enabled: bool, sound_enabled: bool = True, light_enabled: bool = True) -> None:
        """Configure alarm settings."""
        self.tapo.setAlarm(enabled, sound_enabled, light_enabled)

    def move_motor(self, x_deg: float, y_deg: float) -> None:
        """Move camera (PTZ control).

        Args:
            x_deg: Horizontal degrees (-360 to 360)
            y_deg: Vertical degrees (-90 to 90)
        """
        self.tapo.moveMotor(x_deg, y_deg)

    def move_motor_step(self, direction: str) -> None:
        """Move camera one step in direction.

        Args:
            direction: 'up', 'down', 'left', 'right'
        """
        self.tapo.moveMotorStep(direction)

    def get_presets(self) -> dict[str, Any]:
        """Get saved preset positions."""
        return self.tapo.getPresets()

    def set_preset(self, name: str) -> None:
        """Save current position as preset."""
        self.tapo.setPreset(name)

    def go_to_preset(self, preset_id: str) -> None:
        """Move to saved preset position."""
        self.tapo.setPreset(preset_id)

    def reboot(self) -> None:
        """Reboot the camera."""
        self.tapo.reboot()

    def get_rtsp_url(self, stream: str = "hd") -> str:
        """Get RTSP stream URL.

        Args:
            stream: 'hd' for high definition (stream1) or 'sd' for standard (stream2)

        Returns:
            RTSP URL string
        """
        stream_path = "stream1" if stream == "hd" else "stream2"
        return f"rtsp://{self.username}:{self.password}@{self.host}:554/{stream_path}"

    def get_onvif_url(self) -> str:
        """Get ONVIF service URL."""
        return f"http://{self.host}:2020/onvif/device_service"

    def get_recordings(self, date: str) -> list[dict[str, Any]]:
        """Get list of recordings for a specific date.

        Args:
            date: Date in YYYYMMDD format

        Returns:
            List of recording metadata
        """
        return self.tapo.getRecordings(date)

    @classmethod
    def from_env(cls) -> "TapoCamera":
        """Create camera instance from environment variables."""
        from dotenv import load_dotenv
        load_dotenv()

        host = os.getenv("TAPO_HOST")
        username = os.getenv("TAPO_USERNAME")
        password = os.getenv("TAPO_PASSWORD")
        cloud_password = os.getenv("TPLINK_CLOUD_PASSWORD")

        if not all([host, username, password]):
            raise ValueError(
                "Missing required environment variables: TAPO_HOST, TAPO_USERNAME, TAPO_PASSWORD"
            )

        return cls(host, username, password, cloud_password)
