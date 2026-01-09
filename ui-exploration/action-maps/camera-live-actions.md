# Camera Live Screen - User Actions Map

**Screen:** camera-live
**Resolution:** 320x640
**Worker:** worker-2

## Quick Reference - Tap Coordinates

### Header Actions
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Go Back | tap(24, 57) | [0,33][48,81] | Returns to home screen |
| Device Settings | tap(296, 57) | [272,33][320,81] | Opens device settings |

### Video Player Controls (on video overlay)
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Multi-View | tap(68, 244) | [44,220][92,268] | Switch to multi-camera view |
| Video Mode | tap(160, 244) | [136,220][184,268] | Toggle Auto/Day/Night mode |
| Fullscreen | tap(252, 244) | [228,220][276,268] | Enter fullscreen landscape |

### Media Toolbar
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Take Photo | tap(50, 302) | [26,278][74,326] | Capture photo from live feed |
| Record Video | tap(123, 302) | [99,278][147,326] | Start/stop manual recording |
| Mic Volume | tap(197, 302) | [173,278][221,326] | Camera microphone volume |
| Voice Call | tap(270, 302) | [246,278][294,326] | Two-way audio call |

### Control Panel - Row 1
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Talk (PTT) | tap(64, 391) | [16,350][112,433] | Push-to-talk |
| Pan & Tilt | tap(160, 391) | [112,350][208,433] | Open PTZ controls |
| Alarm Toggle | tap(256, 391) | [208,350][304,433] | Toggle detection alarm |

### Control Panel - Row 2
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Privacy Mode | tap(64, 474) | [16,433][112,516] | Toggle privacy mode |
| Tapo Care | tap(160, 474) | [112,433][208,516] | Open Tapo Care info |

### Storage Section
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Playback & Download | tap(160, 576) | [16,545][304,608] | Open playback screen |
| Cloud Storage | tap(160, 632) | [16,624][304,640] | Tapo Care cloud promo |
| Dismiss Promo | tap(280, 632) | [256,624][304,640] | Close cloud promo |

## ADB Command Sequences

### Go Back to Home
```bash
adb -s emulator-5556 shell input tap 24 57
sleep 2
```

### Open Device Settings
```bash
adb -s emulator-5556 shell input tap 296 57
sleep 3
```

### Take a Photo
```bash
adb -s emulator-5556 shell input tap 50 302
sleep 1
```

### Start/Stop Recording
```bash
adb -s emulator-5556 shell input tap 123 302
sleep 1
```

### Toggle Privacy Mode
```bash
adb -s emulator-5556 shell input tap 64 474
sleep 2
```

### Toggle Detection Alarm
```bash
adb -s emulator-5556 shell input tap 256 391
sleep 1
```

### Open Pan & Tilt Controls
```bash
adb -s emulator-5556 shell input tap 160 391
sleep 2
```

### Enter Fullscreen
```bash
adb -s emulator-5556 shell input tap 252 244
sleep 1
```

### Open Playback
```bash
adb -s emulator-5556 shell input tap 160 576
sleep 3
```

## Element Identifiers

| Element | Resource ID | Content-Desc |
|---------|-------------|--------------|
| Back button | `com.tplink.iot:id/btn_back` | "Back" |
| Title | `com.tplink.iot:id/title` | - |
| Settings | `com.tplink.iot:id/action_settings` | "Device Settings" |
| Multi-view | `com.tplink.iot:id/tool_view` | "Switch to Multi-View" |
| Video mode | `com.tplink.iot:id/tv_infrared_mode` | "Video Mode, Auto" |
| Fullscreen | `com.tplink.iot:id/tool_full_screen` | "Fullscreen" |
| Photo | `com.tplink.iot:id/tool_pic` | "Take Photo" |
| Record | `com.tplink.iot:id/tool_video` | "Record Video" |
| Sound | `com.tplink.iot:id/tool_sound` | "Camera's Microphone Volume" |
| Voice | `com.tplink.iot:id/tool_voice_call` | "Voice Call" |
| Talk | `com.tplink.iot:id/talk_tv` | "Talk" |
| Pan & Tilt | `com.tplink.iot:id/control_tv` | "Pan and Tilt Controls" |
| Alarm | `com.tplink.iot:id/call_tv` | "Detection Alarm, Off" |
| Privacy | `com.tplink.iot:id/privacy_tv` | "Privacy Mode, Off" |
| Tapo Care | `com.tplink.iot:id/alerts_tv` | "Tapo Care" |
| Playback | `com.tplink.iot:id/playback_and_download` | "Playback & Download" |

## State Detection

Check content-desc for current states:
- **Alarm state**: `call_tv` content-desc contains "On" or "Off"
- **Privacy state**: `privacy_tv` content-desc contains "On" or "Off"
- **Video mode**: `tv_infrared_mode` content-desc contains "Auto", "Day", or "Night"
- **Streaming**: `accessibility_mask_view` content-desc contains "Streaming"

## Navigation Graph

```
camera-live
├── home (tap back)
├── device-settings (tap settings)
├── multi-view (tap multi-view)
├── fullscreen (tap fullscreen)
├── pan-tilt-controls (tap Pan & Tilt)
├── tapo-care (tap Tapo Care)
└── playback-download (tap Playback)
```

## Common Automation Sequences

### Check and Enable Privacy Mode
```bash
# Dump UI to check state
adb -s emulator-5556 shell uiautomator dump /sdcard/ui.xml
# Parse for "Privacy Mode, Off" in content-desc
# If Off, tap to enable
adb -s emulator-5556 shell input tap 64 474
```

### Capture Photo Sequence
```bash
# Wait for stream to be ready
sleep 2
# Take photo
adb -s emulator-5556 shell input tap 50 302
# Wait for capture
sleep 1
```

## Notes
- Device settings may cause ANR if camera is not reachable
- Video stream must be active for photo/record to work
- Privacy mode toggle has ~2 second delay
- Fullscreen rotates to landscape
