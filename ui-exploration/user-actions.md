# User Actions Mapping for Tapo App Automation

This file provides quick-reference tap coordinates and ADB commands for automating the Tapo app.

## Screen Resolution
- Emulator resolution: **320x640**
- All coordinates below are in this resolution

---

## Home Screen

**Screenshot:** `screenshots/home.png`

### Navigation Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Open Camera (Tapo_C210) | `85, 220` | `adb shell input tap 85 220` |
| Toggle Privacy Mode | `130, 184` | `adb shell input tap 130 184` |
| Open Notifications | `248, 48` | `adb shell input tap 248 48` |
| Open Add Device | `296, 48` | `adb shell input tap 296 48` |
| Open Family Picker | `45, 48` | `adb shell input tap 45 48` |
| Switch to Favorites Tab | `60, 127` | `adb shell input tap 60 127` |
| Switch to All Devices Tab | `170, 127` | `adb shell input tap 170 127` |
| Open More Rooms | `292, 127` | `adb shell input tap 292 127` |

### Bottom Navigation (from any screen)
| Tab | Tap Coordinates | ADB Command |
|-----|-----------------|-------------|
| Home | `32, 615` | `adb shell input tap 32 615` |
| Cameras | `96, 615` | `adb shell input tap 96 615` |
| Vacuums | `160, 615` | `adb shell input tap 160 615` |
| Smart | `224, 615` | `adb shell input tap 224 615` |
| Me | `288, 615` | `adb shell input tap 288 615` |

---

## Camera Live Screen

**Screenshot:** `screenshots/camera-live.png`

### Navigation Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Go Back | `24, 57` | `adb shell input tap 24 57` |
| Open Device Settings | `296, 57` | `adb shell input tap 296 57` |

### Video Controls (Overlay)
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Multi-View | `68, 244` | `adb shell input tap 68 244` |
| Video Mode (Day/Night/Auto) | `160, 244` | `adb shell input tap 160 244` |
| Fullscreen | `252, 244` | `adb shell input tap 252 244` |

### Media Controls
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Take Photo | `50, 302` | `adb shell input tap 50 302` |
| Record Video | `123, 302` | `adb shell input tap 123 302` |
| Mic Volume | `197, 302` | `adb shell input tap 197 302` |
| Voice Call | `270, 302` | `adb shell input tap 270 302` |

### Control Panel
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Talk | `64, 392` | `adb shell input tap 64 392` |
| Pan & Tilt | `160, 392` | `adb shell input tap 160 392` |
| Detection Alarm Toggle | `256, 392` | `adb shell input tap 256 392` |
| Privacy Mode Toggle | `64, 474` | `adb shell input tap 64 474` |
| Tapo Care | `160, 474` | `adb shell input tap 160 474` |

### Bottom Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Playback & Download | `160, 577` | `adb shell input tap 160 577` |

---

## Cameras Tab Screen

**Screenshot:** `screenshots/cameras-tab.png`

### Navigation Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Add Camera | `296, 48` | `adb shell input tap 296 48` |
| Switch to Cloud Activity | `176, 96` | `adb shell input tap 176 96` |
| Home Mode | `84, 439` | `adb shell input tap 84 439` |
| Away Mode | `235, 439` | `adb shell input tap 235 439` |
| Home Mode Settings | `129, 419` | `adb shell input tap 129 419` |
| Away Mode Settings | `280, 419` | `adb shell input tap 280 419` |
| Close Tapo Care Banner | `280, 160` | `adb shell input tap 280 160` |

---

## Me Tab (Profile/Settings) Screen

**Screenshot:** `screenshots/tapo-me-tab-profile-settings-account-worker1.png`

### Navigation Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| View Account/Profile | `160, 133` | `adb shell input tap 160 133` |
| Tapo Care Subscription | `160, 236` | `adb shell input tap 160 236` |
| Playback & Download | `160, 354` | `adb shell input tap 160 354` |
| Camera Memory | `160, 410` | `adb shell input tap 160 410` |
| Firmware Update | `160, 482` | `adb shell input tap 160 482` |
| Notifications Settings | `160, 538` | `adb shell input tap 160 538` |
| Device Sharing | `160, 578` | `adb shell input tap 160 578` |

---

## Common Automation Sequences

### Sequence: Home -> Camera Live -> Take Photo
```bash
# From home, open camera
adb shell input tap 85 220
sleep 3

# Wait for video to load, take photo
adb shell input tap 50 302
```

### Sequence: Toggle Privacy Mode (from Home)
```bash
# Quick toggle from device card
adb shell input tap 130 184
```

### Sequence: Home -> Camera Live -> Pan & Tilt
```bash
# Open camera
adb shell input tap 85 220
sleep 3

# Open PTZ controls
adb shell input tap 160 392
```

### Sequence: Navigate to Playback
```bash
# From home, open camera
adb shell input tap 85 220
sleep 3

# Open playback
adb shell input tap 160 577
```

---

## Activity References

| Screen | Activity |
|--------|----------|
| Home | `com.tplink.iot/.view.main.MainActivity` |
| Camera Live | `com.tplink.iot/.view.ipcamerav3.play.VideoPlayV3Activity` |
| Device Settings | `com.tplink.iot/.view.ipcamera.settingv2.view.CameraSettingsActivityV2` |
| Cameras Tab | `com.tplink.iot/.view.main.MainActivity` (same activity, different tab) |

## Launch App
```bash
adb shell monkey -p com.tplink.iot -c android.intent.category.LAUNCHER 1
```

## Force Restart App
```bash
adb shell am force-stop com.tplink.iot && sleep 1 && adb shell monkey -p com.tplink.iot -c android.intent.category.LAUNCHER 1
```

## Check Current Activity
```bash
adb shell dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'
```

## Dump UI (for debugging)
```bash
adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml
```
