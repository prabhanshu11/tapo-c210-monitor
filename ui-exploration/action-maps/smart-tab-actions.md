# Smart Tab - User Actions Map

**Screen:** smart-tab
**Resolution:** 320x640
**Worker:** worker-2

## Quick Reference - Tap Coordinates

### Header Actions
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| History | tap(248, 48) | [224,24][272,72] | View automation execution history |
| Add Smart Action | tap(296, 48) | [272,24][320,72] | Create new shortcut or automation |

### Tab Navigation
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Recommended Tab | tap(79, 98) | [6,72][153,124] | View recommended templates |
| Shortcuts Tab | tap(204, 98) | [153,72][255,124] | View all shortcuts |
| Automation Tab | tap(287, 98) | [255,72][320,124] | View all automations |

### Shortcut Cards
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Leave Home | tap(98, 290) | [16,157][181,423] | Turn off all devices |
| Arrive Home | tap(256, 290) | [193,157][320,423] | Turn on all devices |

### Automation Cards
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Tap to Alarm | tap(160, 533) | [16,476][304,590] | Alarm automation setup |

### Navigation
| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Home Tab | tap(32, 615) | [0,590][64,640] | Switch to home |
| Cameras Tab | tap(96, 615) | [64,590][128,640] | Switch to cameras |
| Me Tab | tap(288, 615) | [256,590][320,640] | Switch to profile |

## ADB Command Sequences

### Open History
```bash
adb -s emulator-5556 shell input tap 248 48
sleep 2
```

### Add New Smart Action
```bash
adb -s emulator-5556 shell input tap 296 48
sleep 2
```

### Switch to Shortcuts View
```bash
adb -s emulator-5556 shell input tap 204 98
sleep 1
```

### Switch to Automation View
```bash
adb -s emulator-5556 shell input tap 287 98
sleep 1
```

### Configure Leave Home Shortcut
```bash
adb -s emulator-5556 shell input tap 98 290
sleep 2
```

### Configure Arrive Home Shortcut
```bash
adb -s emulator-5556 shell input tap 256 290
sleep 2
```

### Configure Tap to Alarm
```bash
adb -s emulator-5556 shell input tap 160 533
sleep 2
```

### Pull to Refresh
```bash
adb -s emulator-5556 shell input swipe 160 300 160 500 500
sleep 2
```

## Element Identifiers

| Element | Resource ID | Content-Desc |
|---------|-------------|--------------|
| History | `com.tplink.iot:id/smart_history_action` | "History" |
| Add | `com.tplink.iot:id/smart_add_action` | "Add Smart Action" |
| Tab Layout | `com.tplink.iot:id/smart_tab` | - |
| ViewPager | `com.tplink.iot:id/smart_view_pager` | - |
| Shortcut List | `com.tplink.iot:id/rv_shortcut` | - |
| Automation List | `com.tplink.iot:id/rv_automation` | - |
| Leave Home | `com.tplink.iot:id/cv_root` | "Leave Home, Turn off all your Tapo devices..." |
| Arrive Home | `com.tplink.iot:id/cv_root` | "Arrive Home, Turn on all your Tapo devices..." |
| Tap to Alarm | `com.tplink.iot:id/layout_automation_item` | "Recommended Automation, Tap to Alarm, 0 devices available" |

## Navigation Graph

```
smart-tab
├── smart-history (tap history)
├── add-smart-action (tap add)
├── shortcuts-view (tap Shortcuts tab)
├── automation-view (tap Automation tab)
├── shortcut-leave-home (tap Leave Home)
├── shortcut-arrive-home (tap Arrive Home)
└── automation-tap-alarm (tap Tap to Alarm)
```

## Tab Content Variations

### Recommended Tab (Default)
Shows both recommended shortcuts and automations in scrollable view

### Shortcuts Tab
Shows only user's created shortcuts (or empty state if none)

### Automation Tab
Shows only user's created automations (or empty state if none)

## Notes
- No camera access needed - stable screen
- Content is pull-to-refresh enabled
- ViewPager allows swipe between tabs
- Shortcut cards are scrollable horizontally in rv_shortcut
- Automation list is vertical scrolling
