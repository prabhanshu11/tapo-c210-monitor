# Notifications Screen - Worker 2 Documentation

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T06:59:00Z
**Package:** com.tplink.iot

## Screen Overview
The Notifications screen showing device alerts and activity history.

## UI Structure

### Toolbar (bounds: [0,24][320,88])

| Element | Resource ID | Type | Text/Content-Desc | Bounds | Clickable |
|---------|-------------|------|-------------------|--------|-----------|
| Back | - | ImageButton | "Back" | [0,28][56,84] | Yes |
| Title | `toolbar_title` | TextView | "Notifications" | [111,32][209,80] | No |
| Read All | `action_clear` | Button | "Read all" | [224,32][272,80] | Yes |
| Settings | `action_settings` | Button | "Notification Settings" | [272,32][320,80] | Yes |

### Content Area (bounds: [0,88][320,640])

| Element | Resource ID | Type | Description |
|---------|-------------|------|-------------|
| Refresh Layout | `refresh_layout` | ViewGroup | Pull-to-refresh container |
| Scroll View | `nsv` | ScrollView | Scrollable notification list |
| Content Frame | `fl` | FrameLayout | Notification items container |

## Navigation Paths

### From this screen:
- **Tap Back** -> Return to home
- **Tap Read All** -> Mark all notifications as read
- **Tap Settings** -> `notification-settings` (notification preferences)
- **Pull down** -> Refresh notifications

## Quick Reference - Tap Coordinates

| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Go Back | tap(28, 56) | [0,28][56,84] | Return to previous screen |
| Read All | tap(248, 56) | [224,32][272,80] | Mark all as read |
| Settings | tap(296, 56) | [272,32][320,80] | Notification settings |

## ADB Command Sequences

### Go Back
```bash
adb -s emulator-5556 shell input tap 28 56
sleep 2
```

### Read All Notifications
```bash
adb -s emulator-5556 shell input tap 248 56
sleep 1
```

### Open Notification Settings
```bash
adb -s emulator-5556 shell input tap 296 56
sleep 2
```

## Discovered Screens
- `notification-settings` - Tap settings button [272,32][320,80]

## Key Resource IDs
- `cl` - Main constraint layout
- `toolbar` - Toolbar container
- `toolbar_title` - Screen title
- `action_clear` - Read all button
- `action_settings` - Settings button
- `refresh_layout` - Pull-to-refresh
- `nsv` - Nested scroll view
- `fl` - Frame layout for content

## Notes
- Screen supports pull-to-refresh
- Shows notification history from devices
- Settings allow configuring push notification preferences
- No camera access needed - stable screen
