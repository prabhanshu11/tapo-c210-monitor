# Family Picker Popup - Worker 2 Documentation

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T07:01:00Z
**Package:** com.tplink.iot

## Screen Overview
A popup menu that appears when tapping the home name selector. Allows switching between homes/families and accessing home settings.

## UI Structure (Popup Menu)

### Popup Container (bounds: [8,78][228,192])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Selected |
|---------|-------------|------|------|--------------|--------|----------|
| Family List | `recycle_view` | RecyclerView | - | - | [8,82][228,136] | - |
| My Home Item | - | Button | "My home" | "My home" | [8,82][228,136] | Yes |
| Check Icon | `img_family_select` | ImageView | - | - | [24,97][48,121] | - |
| Family Name | `tv_family_name` | TextView | "My home" | - | [60,98][204,120] | - |
| Home Settings | `layout_home_setting` | Button | "Home Settings" | "Home Settings" | [8,136][228,188] | No |
| Settings Text | `tv_setting` | TextView | "Home Settings" | - | [8,150][188,174] | - |

## Navigation Paths

### From this popup:
- **Tap Home Item** -> Select that home (if multiple homes)
- **Tap Home Settings** -> `home-settings` (manage rooms, members)
- **Tap outside** -> Dismiss popup

## Quick Reference - Tap Coordinates

| Action | Tap Point | Bounds | Description |
|--------|-----------|--------|-------------|
| Select My Home | tap(118, 109) | [8,82][228,136] | Select this home |
| Home Settings | tap(118, 162) | [8,136][228,188] | Open home settings |
| Dismiss | tap(280, 300) | Outside popup | Close popup |

## ADB Command Sequences

### Open Family Picker
```bash
# From home screen, tap home selector
adb -s emulator-5556 shell input tap 55 48
sleep 1
```

### Open Home Settings
```bash
# With popup open
adb -s emulator-5556 shell input tap 118 162
sleep 2
```

### Dismiss Popup
```bash
adb -s emulator-5556 shell input tap 280 300
sleep 1
```

## Discovered Screens
- `home-settings` - Tap Home Settings [8,136][228,188]

## Key Resource IDs
- `cv_root` - Card view container
- `ll_root` - Linear layout root
- `recycle_view` - Family list RecyclerView
- `img_family_select` - Selection check icon
- `tv_family_name` - Family name text
- `layout_home_setting` - Home settings button
- `tv_setting` - Settings label

## Notes
- Popup appears at top-left near the home selector
- Currently only "My home" is available
- Users can add more homes via Home Settings
- Selected home shows check mark icon
- Clicking outside dismisses the popup
