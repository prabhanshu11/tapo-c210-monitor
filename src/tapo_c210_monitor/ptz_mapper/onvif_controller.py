"""ONVIF PTZ Controller for Tapo C210.

Provides pan/tilt control via ONVIF protocol (port 2020).
"""

import os
import time
from dataclasses import dataclass
from typing import Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)


@dataclass
class PTZPosition:
    """Current PTZ position (if camera supports position reporting)."""
    pan: float  # -1.0 to 1.0 (normalized) or degrees
    tilt: float  # -1.0 to 1.0 (normalized) or degrees
    zoom: float = 1.0  # 1.0 = no zoom


@dataclass
class PTZLimits:
    """PTZ movement limits."""
    pan_min: float
    pan_max: float
    tilt_min: float
    tilt_max: float


class ONVIFPTZController:
    """Control camera PTZ via ONVIF protocol."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 2020,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.host = host or os.getenv("TAPO_HOST", "192.168.29.183")
        self.port = port
        self.username = username or os.getenv("TAPO_USERNAME", "")
        self.password = password or os.getenv("TAPO_PASSWORD", "")

        self.camera = None
        self.ptz_service = None
        self.media_service = None
        self.profile_token = None

        # Capabilities discovered during connect
        self.supports_absolute_move = False
        self.supports_relative_move = False
        self.supports_continuous_move = False
        self.supports_position_feedback = False
        self.ptz_limits: Optional[PTZLimits] = None

    def connect(self) -> bool:
        """Connect to camera ONVIF service and discover capabilities."""
        try:
            from onvif import ONVIFCamera

            print(f"Connecting to ONVIF at {self.host}:{self.port}...")
            self.camera = ONVIFCamera(
                self.host,
                self.port,
                self.username,
                self.password
            )

            # Get services
            self.ptz_service = self.camera.create_ptz_service()
            self.media_service = self.camera.create_media_service()

            # Get profile
            profiles = self.media_service.GetProfiles()
            if not profiles:
                print("No media profiles found")
                return False

            self.profile_token = profiles[0].token
            print(f"Using profile: {self.profile_token}")

            # Discover PTZ capabilities
            self._discover_capabilities()

            return True

        except Exception as e:
            print(f"ONVIF connection failed: {e}")
            return False

    def _discover_capabilities(self):
        """Discover what PTZ operations the camera supports."""
        try:
            # Get PTZ configuration
            configs = self.ptz_service.GetConfigurations()
            if configs:
                config = configs[0]
                print(f"PTZ Config: {config.Name}")

            # Get PTZ node (contains capabilities)
            nodes = self.ptz_service.GetNodes()
            if nodes:
                node = nodes[0]
                print(f"PTZ Node: {node.Name}")

                # Check supported operations
                if hasattr(node, 'SupportedPTZSpaces'):
                    spaces = node.SupportedPTZSpaces

                    if hasattr(spaces, 'AbsolutePanTiltPositionSpace') and spaces.AbsolutePanTiltPositionSpace:
                        self.supports_absolute_move = True
                        space = spaces.AbsolutePanTiltPositionSpace[0]
                        self.ptz_limits = PTZLimits(
                            pan_min=space.XRange.Min,
                            pan_max=space.XRange.Max,
                            tilt_min=space.YRange.Min,
                            tilt_max=space.YRange.Max,
                        )
                        print(f"  AbsoluteMove: YES (pan {self.ptz_limits.pan_min} to {self.ptz_limits.pan_max})")

                    if hasattr(spaces, 'RelativePanTiltTranslationSpace') and spaces.RelativePanTiltTranslationSpace:
                        self.supports_relative_move = True
                        print("  RelativeMove: YES")

                    if hasattr(spaces, 'ContinuousPanTiltVelocitySpace') and spaces.ContinuousPanTiltVelocitySpace:
                        self.supports_continuous_move = True
                        print("  ContinuousMove: YES")

            # Test position feedback
            try:
                status = self.ptz_service.GetStatus({'ProfileToken': self.profile_token})
                if status and hasattr(status, 'Position') and status.Position:
                    self.supports_position_feedback = True
                    pos = status.Position
                    if hasattr(pos, 'PanTilt') and pos.PanTilt:
                        print(f"  PositionFeedback: YES (current: pan={pos.PanTilt.x}, tilt={pos.PanTilt.y})")
                    else:
                        print("  PositionFeedback: YES (but PanTilt is None)")
                else:
                    print("  PositionFeedback: NO")
            except Exception as e:
                print(f"  PositionFeedback: NO ({e})")

        except Exception as e:
            print(f"Capability discovery error: {e}")
            # Default to continuous move only
            self.supports_continuous_move = True

    def get_position(self) -> Optional[PTZPosition]:
        """Get current PTZ position (if supported)."""
        if not self.supports_position_feedback:
            return None

        try:
            status = self.ptz_service.GetStatus({'ProfileToken': self.profile_token})
            if status and status.Position and status.Position.PanTilt:
                return PTZPosition(
                    pan=status.Position.PanTilt.x,
                    tilt=status.Position.PanTilt.y,
                    zoom=status.Position.Zoom.x if status.Position.Zoom else 1.0
                )
        except Exception as e:
            print(f"GetPosition error: {e}")
        return None

    def move_continuous(self, pan_velocity: float, tilt_velocity: float, duration: float = 1.0):
        """Move camera at specified velocity for duration.

        Args:
            pan_velocity: -1.0 (left) to 1.0 (right)
            tilt_velocity: -1.0 (down) to 1.0 (up)
            duration: How long to move (seconds)
        """
        if not self.ptz_service:
            raise RuntimeError("Not connected")

        request = self.ptz_service.create_type('ContinuousMove')
        request.ProfileToken = self.profile_token
        request.Velocity = {'PanTilt': {'x': pan_velocity, 'y': tilt_velocity}}

        self.ptz_service.ContinuousMove(request)
        time.sleep(duration)
        self.stop()

    def move_absolute(self, pan: float, tilt: float, speed: float = 0.5) -> bool:
        """Move to absolute position (if supported).

        Args:
            pan: Target pan position (within limits)
            tilt: Target tilt position (within limits)
            speed: Movement speed 0.0-1.0

        Returns:
            True if command sent, False if not supported
        """
        if not self.supports_absolute_move:
            print("AbsoluteMove not supported by this camera")
            return False

        try:
            request = self.ptz_service.create_type('AbsoluteMove')
            request.ProfileToken = self.profile_token
            request.Position = {'PanTilt': {'x': pan, 'y': tilt}}
            request.Speed = {'PanTilt': {'x': speed, 'y': speed}}

            self.ptz_service.AbsoluteMove(request)
            return True
        except Exception as e:
            print(f"AbsoluteMove error: {e}")
            return False

    def move_relative(self, pan_delta: float, tilt_delta: float, speed: float = 0.5) -> bool:
        """Move by relative amount (if supported).

        Args:
            pan_delta: Amount to move pan
            tilt_delta: Amount to move tilt
            speed: Movement speed 0.0-1.0

        Returns:
            True if command sent, False if not supported
        """
        if not self.supports_relative_move:
            print("RelativeMove not supported by this camera")
            return False

        try:
            request = self.ptz_service.create_type('RelativeMove')
            request.ProfileToken = self.profile_token
            request.Translation = {'PanTilt': {'x': pan_delta, 'y': tilt_delta}}
            request.Speed = {'PanTilt': {'x': speed, 'y': speed}}

            self.ptz_service.RelativeMove(request)
            return True
        except Exception as e:
            print(f"RelativeMove error: {e}")
            return False

    def stop(self):
        """Stop all PTZ movement."""
        if self.ptz_service:
            self.ptz_service.Stop({'ProfileToken': self.profile_token})

    def pan_left(self, duration: float = 1.0, speed: float = 0.5):
        """Pan camera left."""
        self.move_continuous(-speed, 0, duration)

    def pan_right(self, duration: float = 1.0, speed: float = 0.5):
        """Pan camera right."""
        self.move_continuous(speed, 0, duration)

    def tilt_up(self, duration: float = 1.0, speed: float = 0.5):
        """Tilt camera up."""
        self.move_continuous(0, speed, duration)

    def tilt_down(self, duration: float = 1.0, speed: float = 0.5):
        """Tilt camera down."""
        self.move_continuous(0, -speed, duration)

    def go_home(self) -> bool:
        """Move to home/preset position if supported."""
        try:
            self.ptz_service.GotoHomePosition({'ProfileToken': self.profile_token})
            return True
        except Exception as e:
            print(f"GotoHome not supported: {e}")
            return False


def main():
    """Test ONVIF PTZ controller."""
    ctrl = ONVIFPTZController()

    if not ctrl.connect():
        print("Failed to connect")
        return

    print("\n" + "=" * 50)
    print("CAPABILITIES SUMMARY")
    print("=" * 50)
    print(f"AbsoluteMove: {ctrl.supports_absolute_move}")
    print(f"RelativeMove: {ctrl.supports_relative_move}")
    print(f"ContinuousMove: {ctrl.supports_continuous_move}")
    print(f"PositionFeedback: {ctrl.supports_position_feedback}")

    if ctrl.ptz_limits:
        print(f"\nPTZ Limits:")
        print(f"  Pan: {ctrl.ptz_limits.pan_min} to {ctrl.ptz_limits.pan_max}")
        print(f"  Tilt: {ctrl.ptz_limits.tilt_min} to {ctrl.ptz_limits.tilt_max}")

    # Get current position
    pos = ctrl.get_position()
    if pos:
        print(f"\nCurrent Position: pan={pos.pan}, tilt={pos.tilt}")

    print("\n" + "=" * 50)
    print("MOVEMENT TEST")
    print("=" * 50)

    # Test continuous move
    print("\nPanning RIGHT for 1 second...")
    ctrl.pan_right(1.0, 0.3)

    pos = ctrl.get_position()
    if pos:
        print(f"Position after: pan={pos.pan}, tilt={pos.tilt}")

    time.sleep(1)

    print("\nPanning LEFT for 1 second...")
    ctrl.pan_left(1.0, 0.3)

    pos = ctrl.get_position()
    if pos:
        print(f"Position after: pan={pos.pan}, tilt={pos.tilt}")


if __name__ == "__main__":
    main()
