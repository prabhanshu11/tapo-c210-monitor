"""ONVIF PTZ and Imaging control for Tapo C210 camera."""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from onvif import ONVIFCamera
from zeep.helpers import serialize_object


class IrCutFilterMode(Enum):
    """IR cut filter modes for night vision control."""
    ON = "ON"      # IR cut filter enabled - day mode (blocks IR light)
    OFF = "OFF"    # IR cut filter disabled - night mode (allows IR light)
    AUTO = "AUTO"  # Camera decides based on ambient light


@dataclass
class PTZPosition:
    """Current PTZ position."""
    pan: float  # -1.0 to 1.0
    tilt: float  # -1.0 to 1.0
    zoom: float  # 0.0 to 1.0


class TapoPTZ:
    """ONVIF PTZ controller for Tapo C210."""

    def __init__(self, ip: str, username: str, password: str, port: int = 2020):
        """Initialize PTZ controller.

        Args:
            ip: Camera IP address
            username: Camera account username
            password: Camera account password
            port: ONVIF port (default 2020 for Tapo)
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self._camera: ONVIFCamera | None = None
        self._ptz = None
        self._media = None
        self._imaging = None
        self._profile_token: str | None = None
        self._video_source_token: str | None = None

    def connect(self) -> bool:
        """Connect to camera ONVIF service.

        Returns:
            True if connection successful
        """
        try:
            print(f"[PTZ] Connecting to {self.ip}:{self.port}...")
            self._camera = ONVIFCamera(
                self.ip,
                self.port,
                self.username,
                self.password
            )

            # Get media service and profile
            self._media = self._camera.create_media_service()
            profiles = self._media.GetProfiles()
            if not profiles:
                print("[PTZ] No media profiles found")
                return False

            self._profile_token = profiles[0].token
            print(f"[PTZ] Using profile: {self._profile_token}")

            # Get PTZ service
            self._ptz = self._camera.create_ptz_service()

            # Check PTZ capabilities
            configs = self._ptz.GetConfigurations()
            if configs:
                print(f"[PTZ] PTZ configurations found: {len(configs)}")
            else:
                print("[PTZ] Warning: No PTZ configurations found")

            # Get Imaging service for IR control
            try:
                self._imaging = self._camera.create_imaging_service()
                # Get video source token from profile
                if profiles[0].VideoSourceConfiguration:
                    self._video_source_token = profiles[0].VideoSourceConfiguration.SourceToken
                    print(f"[PTZ] Imaging service available, video source: {self._video_source_token}")
                else:
                    print("[PTZ] Warning: No video source configuration in profile")
            except Exception as e:
                print(f"[PTZ] Imaging service not available: {e}")
                self._imaging = None

            print(f"[PTZ] Connected to {self.ip}")
            return True

        except Exception as e:
            print(f"[PTZ] Connection failed: {e}")
            return False

    def continuous_move(
        self,
        pan_velocity: float = 0.0,
        tilt_velocity: float = 0.0,
        zoom_velocity: float = 0.0
    ):
        """Start continuous movement.

        Args:
            pan_velocity: -1.0 (left) to 1.0 (right)
            tilt_velocity: -1.0 (down) to 1.0 (up)
            zoom_velocity: -1.0 (zoom out) to 1.0 (zoom in)
        """
        if self._ptz is None:
            print("[PTZ] Not connected")
            return

        request = self._ptz.create_type('ContinuousMove')
        request.ProfileToken = self._profile_token
        request.Velocity = {
            'PanTilt': {'x': pan_velocity, 'y': tilt_velocity},
            'Zoom': {'x': zoom_velocity}
        }

        try:
            self._ptz.ContinuousMove(request)
        except Exception as e:
            print(f"[PTZ] ContinuousMove failed: {e}")

    def stop(self):
        """Stop all PTZ movement."""
        if self._ptz is None:
            return

        try:
            self._ptz.Stop({'ProfileToken': self._profile_token})
        except Exception as e:
            print(f"[PTZ] Stop failed: {e}")

    def move_timed(
        self,
        pan_velocity: float,
        tilt_velocity: float,
        duration: float
    ):
        """Move for a specific duration then stop.

        Args:
            pan_velocity: -1.0 to 1.0
            tilt_velocity: -1.0 to 1.0
            duration: Movement duration in seconds
        """
        self.continuous_move(pan_velocity, tilt_velocity)
        time.sleep(duration)
        self.stop()

    def pan_left(self, duration: float = 0.5, speed: float = 0.5):
        """Pan left for duration."""
        self.move_timed(-speed, 0, duration)

    def pan_right(self, duration: float = 0.5, speed: float = 0.5):
        """Pan right for duration."""
        self.move_timed(speed, 0, duration)

    def tilt_up(self, duration: float = 0.5, speed: float = 0.5):
        """Tilt up for duration."""
        self.move_timed(0, speed, duration)

    def tilt_down(self, duration: float = 0.5, speed: float = 0.5):
        """Tilt down for duration."""
        self.move_timed(0, -speed, duration)

    def get_position(self) -> PTZPosition | None:
        """Get current PTZ position.

        Returns:
            PTZPosition or None if not available
        """
        if self._ptz is None:
            return None

        try:
            status = self._ptz.GetStatus({'ProfileToken': self._profile_token})
            pos = serialize_object(status.Position)

            return PTZPosition(
                pan=pos.get('PanTilt', {}).get('x', 0.0),
                tilt=pos.get('PanTilt', {}).get('y', 0.0),
                zoom=pos.get('Zoom', {}).get('x', 0.0)
            )
        except Exception as e:
            print(f"[PTZ] GetStatus failed: {e}")
            return None

    def absolute_move(self, pan: float, tilt: float, zoom: float = 0.0):
        """Move to absolute position.

        Args:
            pan: -1.0 to 1.0
            tilt: -1.0 to 1.0
            zoom: 0.0 to 1.0
        """
        if self._ptz is None:
            print("[PTZ] Not connected")
            return

        request = self._ptz.create_type('AbsoluteMove')
        request.ProfileToken = self._profile_token
        request.Position = {
            'PanTilt': {'x': pan, 'y': tilt},
            'Zoom': {'x': zoom}
        }

        try:
            self._ptz.AbsoluteMove(request)
            # Wait for movement to complete
            time.sleep(1.5)
        except Exception as e:
            print(f"[PTZ] AbsoluteMove failed (may not be supported): {e}")
            # Fall back to continuous move approximation
            self._move_to_position_continuous(pan, tilt)

    def _move_to_position_continuous(self, target_pan: float, target_tilt: float):
        """Approximate absolute move using continuous movement.

        This is a fallback when AbsoluteMove is not supported.
        """
        # First, go to home position (center)
        print("[PTZ] Using continuous move fallback...")

        # Move to approximate position using timing
        # This is imprecise but works without absolute positioning
        if target_pan < 0:
            self.pan_left(duration=abs(target_pan) * 2)
        elif target_pan > 0:
            self.pan_right(duration=abs(target_pan) * 2)

        if target_tilt < 0:
            self.tilt_down(duration=abs(target_tilt) * 2)
        elif target_tilt > 0:
            self.tilt_up(duration=abs(target_tilt) * 2)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.stop()

    # ==========================================================================
    # IR Cut Filter / Night Vision Control (ONVIF Imaging Service)
    # ==========================================================================

    def get_ir_cut_filter(self) -> IrCutFilterMode | None:
        """Get current IR cut filter mode.

        Returns:
            IrCutFilterMode or None if not available
        """
        if self._imaging is None or self._video_source_token is None:
            print("[IR] Imaging service not available")
            return None

        try:
            settings = self._imaging.GetImagingSettings({
                'VideoSourceToken': self._video_source_token
            })
            ir_filter = serialize_object(settings).get('IrCutFilter')
            if ir_filter:
                return IrCutFilterMode(ir_filter)
            print("[IR] IrCutFilter not in settings response")
            return None
        except Exception as e:
            print(f"[IR] GetImagingSettings failed: {e}")
            return None

    def set_ir_cut_filter(self, mode: IrCutFilterMode) -> bool:
        """Set IR cut filter mode.

        Args:
            mode: IrCutFilterMode.ON (day), OFF (night), or AUTO

        Returns:
            True if successful
        """
        if self._imaging is None or self._video_source_token is None:
            print("[IR] Imaging service not available")
            return False

        try:
            # First get current settings to preserve other values
            current = self._imaging.GetImagingSettings({
                'VideoSourceToken': self._video_source_token
            })

            # Update IrCutFilter
            request = self._imaging.create_type('SetImagingSettings')
            request.VideoSourceToken = self._video_source_token
            request.ImagingSettings = {'IrCutFilter': mode.value}
            request.ForcePersistence = True

            self._imaging.SetImagingSettings(request)
            print(f"[IR] Set IrCutFilter to {mode.value}")
            return True

        except Exception as e:
            print(f"[IR] SetImagingSettings failed: {e}")
            return False

    def enable_night_vision(self) -> bool:
        """Enable night vision (disable IR cut filter).

        When IR cut filter is OFF, infrared light passes through,
        allowing the camera to see in the dark using IR LEDs.

        Returns:
            True if successful
        """
        print("[IR] Enabling night vision (IrCutFilter=OFF)...")
        return self.set_ir_cut_filter(IrCutFilterMode.OFF)

    def disable_night_vision(self) -> bool:
        """Disable night vision (enable IR cut filter).

        When IR cut filter is ON, it blocks infrared light,
        providing normal daytime color video.

        Returns:
            True if successful
        """
        print("[IR] Disabling night vision (IrCutFilter=ON)...")
        return self.set_ir_cut_filter(IrCutFilterMode.ON)

    def auto_night_vision(self) -> bool:
        """Set night vision to auto mode.

        The camera automatically switches between day/night mode
        based on ambient light levels.

        Returns:
            True if successful
        """
        print("[IR] Setting night vision to AUTO...")
        return self.set_ir_cut_filter(IrCutFilterMode.AUTO)
