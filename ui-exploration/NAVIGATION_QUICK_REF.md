# Navigation Quick Reference

## CRITICAL: Coordinate System

**Screen Resolution**: 320x640 dp (NOT 720x1280 physical pixels!)

`adb shell input tap` uses **dp coordinates**, not physical pixels. All coordinates in this document are in dp.

---

## Launch → Camera Live View

```bash
# 1. Launch app
adb shell am start -n com.tplink.iot/.view.welcome.StartupActivity

# 2. Wait for home screen (MainActivity)
sleep 3

# 3. Verify we're on home screen
adb shell uiautomator dump /sdcard/ui.xml
adb shell grep -o 'text="My home"' /sdcard/ui.xml && echo "On home screen"

# 4. Tap camera card [16,160][154,280] - center at (85, 220)
adb shell input tap 85 220

# 5. Wait for camera-live (VideoPlayV3Activity)
sleep 3

# 6. Verify we're on camera screen
adb shell uiautomator dump /sdcard/ui.xml
adb shell grep -o 'accessibility_mask_view' /sdcard/ui.xml && echo "On camera live view"
```

---

## Key Coordinates (320x640 dp)

### Home Screen (MainActivity)
| Element | Bounds | Tap Point | Description |
|---------|--------|-----------|-------------|
| Camera Card | [16,160][154,280] | tap 85 220 | Opens camera live view |
| Privacy Toggle | [106,160][154,208] | tap 130 184 | Toggle privacy mode |
| Notifications | [224,24][272,72] | tap 248 48 | Open notifications |
| Cameras Tab | [64,590][128,640] | tap 96 615 | Bottom nav |
| Me Tab | [256,590][320,640] | tap 288 615 | Bottom nav |

### Camera Live View (VideoPlayV3Activity)
| Element | Bounds | Tap Point | Description |
|---------|--------|-----------|-------------|
| Back | [0,33][48,81] | tap 24 57 | Return to home |
| Settings | [272,33][320,81] | tap 296 57 | Device settings |
| Fullscreen | [228,220][276,268] | tap 252 244 | Landscape mode |
| Multi-View | [44,220][92,268] | tap 68 244 | Multi-camera view |
| Video Mode | [136,220][184,268] | tap 160 244 | Auto/Day/Night |
| Take Photo | [26,278][74,326] | tap 50 302 | Capture snapshot |
| Record | [99,278][147,326] | tap 123 302 | Start/stop recording |
| Pan & Tilt | [112,350][208,433] | tap 160 391 | Open PTZ controls |
| Privacy Mode | [16,433][112,516] | tap 64 474 | Toggle privacy |
| Playback | [16,545][304,608] | tap 160 576 | Open playback |

### PTZ Controls (Pan-Tilt-Zoom Popup)
| Element | Tap Point | Description |
|---------|-----------|-------------|
| Left | tap 108 592 | Pan left |
| Right | tap 208 592 | Pan right |
| Up | tap 160 541 | Tilt up |
| Down | tap 160 625 | Tilt down |

---

## Common Sequences

### Navigate to Camera and Enter Fullscreen
```bash
adb shell am start -n com.tplink.iot/.view.welcome.StartupActivity
sleep 3
adb shell input tap 85 220  # Camera card
sleep 3
adb shell input tap 252 244 # Fullscreen
```

### Take a Photo
```bash
adb shell am start -n com.tplink.iot/.view.welcome.StartupActivity
sleep 3
adb shell input tap 85 220  # Camera card
sleep 3
adb shell input tap 50 302  # Take photo
sleep 1
```

### Open PTZ Controls
```bash
adb shell input tap 160 391 # Pan & Tilt button
sleep 1
# Now use PTZ coordinates
```

---

## Screen Detection

```bash
# Get current activity
adb shell dumpsys activity activities | grep mResumedActivity

# Expected outputs:
# MainActivity       = Home screen
# VideoPlayV3Activity = Camera live view
# StartupActivity    = Login/splash screen
```

---

## Troubleshooting

### Taps Not Working
1. Verify coordinates are in dp (320x640), not pixels (720x1280)
2. Check current screen with `adb shell uiautomator dump`
3. Verify emulator is responsive: `adb shell input tap 0 0`

### App Not Starting
```bash
# Force stop and restart
adb shell am force-stop com.tplink.iot
sleep 1
adb shell am start -n com.tplink.iot/.view.welcome.StartupActivity
```

### Screen Changed Unexpectedly
Use UI dump to find current elements:
```bash
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml /tmp/ui.xml
grep -oP 'text="[^"]*"' /tmp/ui.xml | head -20
```
