# PTZ Control for Tapo C210

## Discovery (2026-01-11)

The Tapo C210 exposes full PTZ control via **ONVIF on port 2020**.

### Supported Capabilities

| Feature | Supported | Notes |
|---------|-----------|-------|
| AbsoluteMove | ✅ | Move to exact position (-1.0 to 1.0) |
| RelativeMove | ✅ | Move by delta amount |
| ContinuousMove | ✅ | Velocity-based movement |
| Position Feedback | ✅ | Real-time position via GetStatus |
| Presets | ✅ | Save/recall positions |
| Home Position | ✅ | GotoHomePosition supported |

### Position System

- **Pan**: -1.0 (left) to 1.0 (right)
- **Tilt**: -1.0 (down) to 1.0 (up)
- Values are normalized, not degrees

### Authentication

Uses the **Camera Account** credentials (same as RTSP):
- Username: Set in Tapo app under camera settings
- Password: Set in Tapo app under camera settings

### Why pytapo Failed

The `pytapo` library uses TP-Link's proprietary encrypted API which requires either:
1. TP-Link Cloud password (email/password for TP-Link account)
2. A specific token exchange mechanism

ONVIF bypasses this entirely using the standard protocol.

### About "Pan and Tilt Correction" in Tapo App

The app's calibration feature likely:
1. Re-calibrates internal motor encoder against physical limits
2. Uses proprietary TP-Link protocol (not exposed via ONVIF)
3. Corrects any drift accumulated over time

ONVIF provides position feedback but the internal encoder-to-position mapping is proprietary. For our purposes, position feedback is sufficient.

## Usage

```python
from tapo_c210_monitor.ptz_mapper import ONVIFPTZController

# Connect
ctrl = ONVIFPTZController()
ctrl.connect()

# Get current position
pos = ctrl.get_position()
print(f"Pan: {pos.pan}, Tilt: {pos.tilt}")

# Move to absolute position
ctrl.move_absolute(pan=0.5, tilt=0.0)

# Convenience methods
ctrl.pan_left(duration=1.0)
ctrl.pan_right(duration=1.0)
ctrl.tilt_up(duration=1.0)
ctrl.tilt_down(duration=1.0)

# Go home
ctrl.go_home()
```

## Ports Used

| Port | Protocol | Purpose |
|------|----------|---------|
| 2020 | ONVIF | PTZ control, device info |
| 554 | RTSP | Video stream |
| 443 | HTTPS | Web interface |
| 8800 | Proprietary | TP-Link internal |
