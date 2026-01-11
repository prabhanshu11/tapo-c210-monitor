# Third-Party Compatibility Settings

**Documented:** 2026-01-11
**Package:** com.tplink.iot
**Path:** Me tab > Settings (gear icon) > Third-Party Compatibility
**Screenshots:** `screenshots/2026-01-11-discoveries/01-*.png`, `02-*.png`

## Overview

This settings page enables integration with third-party smart home platforms like **Home Assistant**. When enabled, the camera can be controlled via open-source home automation systems.

**IMPORTANT**: This is different from the "Third-Party Services" popup that appears on app startup (which advertises Alexa/Google/SmartThings integrations). This settings page enables deeper protocol-level compatibility.

## Status: ENABLED (2026-01-11)

User enabled this feature to allow potential RTSP/ONVIF access for home automation integration.

## Screen Details

### Toggle OFF State
- **Header**: "< Third-Party Compatibility"
- **Toggle**: Gray/off
- **Description**: "When enabled, your smart devices integrate seamlessly with third-party ecosystems like Home Assistant, boosting your smart home connectivity."
- **Disclaimer**: "Enabling this feature for compatibility with open-source platforms like Home Assistant may introduce certain privacy risks."

### Enabling - Confirmation Dialog
When toggling ON, a confirmation dialog appears:

**Dialog Title**: "Disclaimer: Enabling this feature for compatibility with open-source platforms like Home Assistant may introduce certain privacy risks."

**Dialog Body**: "This operation will apply to all devices associated with your TP-Link ID, including those in the Tapo & Kasa app."

**Buttons**:
| Button | Position | Action |
|--------|----------|--------|
| Cancel | Left | Dismiss, keep OFF |
| Enable Anyway | Right (blue) | Enable feature |

### Toggle ON State
- Toggle shows blue/enabled
- Description text remains the same
- Feature now active for all devices on account

## Navigation Path

```bash
# From home screen
adb shell input tap 288 615  # Me tab
sleep 2
# Tap gear/settings icon (top right of Me tab)
# Then tap "Third-Party Compatibility" row
```

**Note**: Exact coordinates for settings icon and Third-Party Compatibility row need to be captured via uiautomator dump.

## Implications

### Potential Benefits
1. **Home Assistant Integration**: May enable local control protocols
2. **ONVIF/RTSP**: May open local network ports for video streaming
3. **Local API Access**: Could allow pytapo or similar libraries to connect

### Privacy Considerations
- Opens device to third-party platforms
- Applies to ALL devices on the TP-Link account
- May expose local network endpoints

## Port Scan Results

### Initial Scan (After Enabling - No Reboot)
**Tested 2026-01-11 ~05:20** - IP: 192.168.29.137

All ports closed - Third-Party Compatibility alone doesn't open ports.

### After Camera Reboot + Camera Account Creation
**Tested 2026-01-11 ~05:30** - IP: **192.168.29.183** (IP changed!)

| Port | Protocol | Status |
|------|----------|--------|
| 443 | HTTPS | **OPEN** |
| 554 | RTSP | **OPEN** |
| 2020 | ONVIF | **OPEN** |
| 8800 | Proprietary | **OPEN** |
| 80 | HTTP | closed |

## Complete Setup Steps (Required for RTSP)

1. **Enable Third-Party Compatibility** (this screen)
2. **Create Camera Account** (Advanced Settings > Camera Account)
   - This creates RTSP credentials separate from TP-Link account
3. **Reboot camera** (power cycle required for ports to open)

## RTSP Access Confirmed Working!

```bash
# HD Stream
rtsp://prabhanshu:iamapantar@192.168.29.183/stream1

# SD Stream
rtsp://prabhanshu:iamapantar@192.168.29.183/stream2

# Test with ffprobe
ffprobe "rtsp://prabhanshu:iamapantar@192.168.29.183/stream1"

# Capture frame
ffmpeg -rtsp_transport tcp -i "rtsp://prabhanshu:iamapantar@192.168.29.183/stream1" \
  -frames:v 1 -update 1 /tmp/frame.jpg
```

**Stream Details**:
- Codec: H.264 High Profile
- Resolution: 2304x1296
- Frame rate: 25 fps

## Related Documentation
- `screens/startup-flows.md` - Third-Party Services popup (different feature)
- `screens/me-tab.md` - Me tab navigation
- `SESSION_2026-01-11.md` - Discovery context
