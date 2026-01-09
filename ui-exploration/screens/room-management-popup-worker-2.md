# Room Management Popup - Worker 2 Documentation

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T07:02:00Z
**Package:** com.tplink.iot

## Screen Overview
A popup menu that appears when tapping the "More" button in the device tabs. Offers options to change view mode and manage rooms.

## UI Structure (Popup Menu)

### Popup Container (bounds: [120,159][320,275])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| List View | `tv_linear` | Button | "List View" | "List View" | [122,161][302,217] | Yes |
| Room Settings | `tv_setting` | Button | "Room Settings" | "Room Settings" | [122,217][302,273] | Yes |

## Navigation Paths

### From this popup:
- **Tap List View** -> Switch to list view mode (from grid)
- **Tap Room Settings** -> `room-settings` (add/edit/delete rooms)
- **Tap outside** -> Dismiss popup

## Quick Reference - Tap Coordinates

| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| List View | tap(212, 189) | [122,161][302,217] | Switch to list view |
| Room Settings | tap(212, 245) | [122,217][302,273] | Manage rooms |
| Dismiss | tap(50, 400) | Outside popup | Close popup |

## ADB Command Sequences

### Open Room Management
```bash
# From home screen, tap More button in tabs
adb -s emulator-5556 shell input tap 292 127
sleep 1
```

### Switch to List View
```bash
# With popup open
adb -s emulator-5556 shell input tap 212 189
sleep 1
```

### Open Room Settings
```bash
# With popup open
adb -s emulator-5556 shell input tap 212 245
sleep 2
```

## Discovered Screens
- `room-settings` - Tap Room Settings [122,217][302,273]

## Key Resource IDs
- `tv_linear` - List View button
- `tv_setting` - Room Settings button

## Notes
- Popup appears near the More button
- List View toggles between grid and list display
- Room Settings allows adding/editing rooms
- Clicking outside dismisses the popup
