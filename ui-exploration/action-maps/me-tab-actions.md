# Me Tab - User Actions Map

**Screen:** me-tab
**Resolution:** 320x640
**Worker:** worker-2

## Quick Reference - Tap Coordinates

### Profile Section
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| View Account | tap(160, 133) | [0,92][320,175] | Opens account details/settings |

### Tapo Care Section
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Tapo Care | tap(160, 236) | [16,191][304,281] | Opens cloud subscription info |

### Devices Section
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Playback & Download | tap(160, 354) | [16,326][304,382] | Opens recorded video playback |
| Camera Memory | tap(160, 410) | [16,382][304,438] | Opens SD card management |

### Settings Section
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Firmware Update | tap(160, 482) | [16,454][304,510] | Opens firmware update screen |
| Notifications | tap(160, 538) | [16,510][304,566] | Opens notification settings |
| Device Sharing | tap(160, 578) | [16,566][304,590] | Opens device sharing options |

### Navigation
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Scroll Down | swipe(160, 500, 160, 200, 500) | - | Reveal more options |
| Home Tab | tap(32, 615) | [0,590][64,640] | Switch to home |
| Cameras Tab | tap(96, 615) | [64,590][128,640] | Switch to cameras |

## ADB Command Sequences

### Open Account Details
```bash
adb -s emulator-5556 shell input tap 160 133
sleep 2
```

### Open Tapo Care Subscription
```bash
adb -s emulator-5556 shell input tap 160 236
sleep 2
```

### Open Playback & Download
```bash
adb -s emulator-5556 shell input tap 160 354
sleep 3
```

### Open Camera Memory Settings
```bash
adb -s emulator-5556 shell input tap 160 410
sleep 2
```

### Open Firmware Update
```bash
adb -s emulator-5556 shell input tap 160 482
sleep 2
```

### Open Notification Settings
```bash
adb -s emulator-5556 shell input tap 160 538
sleep 2
```

### Open Device Sharing
```bash
adb -s emulator-5556 shell input tap 160 578
sleep 2
```

### Scroll to Reveal More Options
```bash
adb -s emulator-5556 shell input swipe 160 500 160 200 500
sleep 1
```

### Return to Home Tab
```bash
adb -s emulator-5556 shell input tap 32 615
sleep 2
```

## Element Identifiers

| Element | Resource ID | Content-Desc |
|---------|-------------|--------------|
| Profile Card | `com.tplink.iot:id/cv_head_info` | "mail.prabhanshu, m a i l . p r a b h a n s h u @ g m a i l . c o m , View Account" |
| Username | `com.tplink.iot:id/tv_user_name` | - |
| Email | `com.tplink.iot:id/tv_user_account` | - |
| Tapo Care | `com.tplink.iot:id/rl_tapo_care` | "Tapo Care Subscribe now to enjoy unlimited cloud storage" |
| Playback | `com.tplink.iot:id/tv_playback_download` | "Playback & Download" |
| Camera Memory | `com.tplink.iot:id/tv_camera_memory` | "Camera Memory" |
| Firmware | `com.tplink.iot:id/rl_firmware` | "Firmware Update" |
| Notifications | `com.tplink.iot:id/tv_notification` | "Notifications" |
| Device Share | `com.tplink.iot:id/tv_device_share` | "Device Sharing" |

## Navigation Graph

```
me-tab
├── account-details (tap profile card)
├── tapo-care-subscription (tap Tapo Care)
├── playback-download (tap Playback & Download)
├── camera-memory (tap Camera Memory)
├── firmware-update (tap Firmware Update)
├── notifications-settings (tap Notifications)
├── device-sharing (tap Device Sharing)
└── [scroll for more options]
    ├── app-settings
    ├── help-feedback
    └── about
```

## Scroll-Hidden Options (need to scroll down)
These options are likely below the visible area:
- App Settings
- Help & Feedback
- About
- Log Out

## Full Navigation Sequence from Home to Me Tab
```bash
# Step 1: Tap Me in bottom nav
adb -s emulator-5556 shell input tap 288 615
sleep 2

# Step 2: Dump UI to verify
adb -s emulator-5556 shell uiautomator dump /sdcard/ui.xml

# Step 3: Verify "Me" tab is selected
# Check for selected="true" on tab_me element
```

## Notes
- No camera access needed - stable screen (no ANR)
- Profile card shows logged-in user info
- Screen scrolls to reveal additional settings
- Useful for account management and app configuration
