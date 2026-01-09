# Home Screen - User Actions Map

**Screen:** home
**Resolution:** 320x640
**Worker:** worker-2

## Quick Reference - Tap Coordinates

### Header Actions
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Switch Home | tap(55, 48) | [8,24][214,72] | Opens home/family picker |
| Notifications | tap(248, 48) | [224,24][272,72] | Opens notifications screen |
| Add Device | tap(296, 48) | [272,24][320,72] | Opens add device flow |

### Tab Navigation
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Favorites Tab | tap(59, 127) | [6,112][113,142] | Switch to favorites view |
| All Devices Tab | tap(170, 127) | [113,112][227,142] | Switch to all devices view |
| Bedroom Tab | tap(247, 127) | [227,112][268,142] | Switch to bedroom room view |
| More Rooms | tap(292, 127) | [268,103][316,151] | Opens room management |

### Device Card Actions
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Open Camera Live | tap(85, 220) | [16,160][154,280] | Opens camera live view |
| Toggle Privacy | tap(130, 184) | [106,160][154,208] | Toggle privacy mode on/off |
| Long-press Options | long_press(85, 220, 1000) | [16,160][154,280] | Opens device options menu |

### Bottom Navigation
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Home Tab | tap(32, 615) | [0,590][64,640] | Stay on home (already selected) |
| Cameras Tab | tap(96, 615) | [64,590][128,640] | Switch to cameras view |
| Vacuums Tab | tap(160, 615) | [128,590][192,640] | Switch to vacuums view |
| Smart Tab | tap(224, 615) | [192,590][256,640] | Switch to smart automations |
| Me Tab | tap(288, 615) | [256,590][320,640] | Switch to profile/settings |

## ADB Command Sequences

### Go to Camera Live View
```bash
# From home screen, tap camera card
adb -s emulator-5556 shell input tap 85 220
sleep 3
```

### Toggle Privacy Mode (from home)
```bash
# Tap privacy toggle on device card
adb -s emulator-5556 shell input tap 130 184
sleep 1
```

### Open Notifications
```bash
# Tap notification bell
adb -s emulator-5556 shell input tap 248 48
sleep 2
```

### Open Add Device Flow
```bash
# Tap plus button
adb -s emulator-5556 shell input tap 296 48
sleep 2
```

### Navigate to Cameras Tab
```bash
# Tap cameras in bottom nav
adb -s emulator-5556 shell input tap 96 615
sleep 2
```

### Navigate to Me/Settings Tab
```bash
# Tap Me in bottom nav
adb -s emulator-5556 shell input tap 288 615
sleep 2
```

### Long-press for Device Options
```bash
# Long press on device card (1 second)
adb -s emulator-5556 shell input swipe 85 220 85 220 1000
sleep 1
```

## Element Identifiers for Programmatic Access

| Element | Resource ID | Content-Desc |
|---------|-------------|--------------|
| Home selector | `com.tplink.iot:id/cl_family_name_toolbar` | "Home, My home" |
| Notifications | `com.tplink.iot:id/iv_home_menu_message` | "Notifications" |
| Add button | `com.tplink.iot:id/iv_home_menu_add` | "Add Device or Add Group" |
| Device card | `com.tplink.iot:id/content` | "Tapo_C210_69A3,Bedroom,Privacy Mode is Off" |
| Privacy toggle | `com.tplink.iot:id/device_switch` | - |
| Tab container | `com.tplink.iot:id/tab_layout` | - |
| Bottom nav | `com.tplink.iot:id/bv_bottomNavigation` | - |

## Navigation Graph

```
home
├── camera-live (tap camera card)
│   └── device-settings (tap settings gear)
├── notifications (tap bell icon)
├── add-device (tap + button)
├── family-picker (tap home selector)
├── room-management (tap More)
├── cameras-tab (bottom nav)
├── vacuums-tab (bottom nav)
├── smart-tab (bottom nav)
└── me-tab (bottom nav)
```

## Notes
- All coordinates are for 320x640 resolution
- For different resolutions, calculate: new_x = (original_x / 320) * new_width
- Long press duration: 1000ms minimum
- Wait times: 2-4 seconds for screen transitions, 1 second for toggles
