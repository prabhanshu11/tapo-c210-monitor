# Add Device Popup - Worker 2 Documentation

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T07:00:00Z
**Package:** com.tplink.iot

## Screen Overview
A popup menu that appears when tapping the + button on the home screen. Offers options to add a device or create a group.

## UI Structure (Popup Menu)

### Popup Container (bounds: [149,78][320,194])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Add Device Button | `btn_add_device` | Button | - | "Add Device" | [151,80][304,136] | Yes |
| Add Device Icon | `iv_add_device_in_popup` | ImageView | - | - | [165,96][189,120] | No |
| Add Device Text | `tv_add_device_in_popup` | TextView | "Add Device" | - | [201,97][304,119] | No |
| Add Group Button | `btn_add_group` | Button | - | "Add Group" | [151,136][304,192] | Yes |
| Add Group Icon | `iv_add_group_in_popup` | ImageView | - | - | [165,152][189,176] | No |
| Add Group Text | `tv_add_group_in_popup` | TextView | "Add Group" | - | [201,153][300,175] | No |

## Navigation Paths

### From this popup:
- **Tap Add Device** -> `device-setup-wizard` (add new Tapo device)
- **Tap Add Group** -> `create-group` (create device group)
- **Tap outside** -> Dismiss popup, return to home

## Quick Reference - Tap Coordinates

| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Add Device | tap(227, 108) | [151,80][304,136] | Start device setup |
| Add Group | tap(227, 164) | [151,136][304,192] | Create device group |
| Dismiss | tap(50, 300) | Outside popup | Close popup |

## ADB Command Sequences

### Add New Device
```bash
# From home, open add menu
adb -s emulator-5556 shell input tap 296 48
sleep 1
# Tap Add Device
adb -s emulator-5556 shell input tap 227 108
sleep 2
```

### Create Group
```bash
# From home, open add menu
adb -s emulator-5556 shell input tap 296 48
sleep 1
# Tap Add Group
adb -s emulator-5556 shell input tap 227 164
sleep 2
```

### Dismiss Popup
```bash
adb -s emulator-5556 shell input tap 50 300
sleep 1
```

## Discovered Screens
- `device-setup-wizard` - Tap Add Device [151,80][304,136]
- `create-group` - Tap Add Group [151,136][304,192]

## Key Resource IDs
- `btn_add_device` - Add device button
- `btn_add_group` - Add group button
- `tv_add_device_in_popup` - Add device label
- `tv_add_group_in_popup` - Add group label

## Notes
- Popup appears at top-right of screen near the + button
- Clicking outside the popup dismisses it
- This is a floating menu, not a full screen
- No camera access needed - stable popup
