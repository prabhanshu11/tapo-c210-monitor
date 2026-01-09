# Vacuums Tab Documentation (Worker-1)

**Activity:** `com.tplink.iot/.view.main.MainActivity` (same as home, different tab)
**Screen Resolution:** 320x640
**Documented:** 2026-01-09

## Screen Structure (Empty State)

### Header Section
| Element | Resource ID | Bounds | Content-desc | Clickable |
|---------|-------------|--------|--------------|-----------|
| Add Robot Vacuum | `iv_add` | [272,24][320,72] | "Add Robot Vacuum" | Yes |

### Empty State Content
**Container:** `layout_empty` - bounds [0,72][320,590]

| Element | Resource ID | Bounds | Text |
|---------|-------------|--------|------|
| Empty Image | `iv_empty` | [40,219][280,365] | - |
| Title | `tv_title` | [0,385][320,408] | "Welcome to Robot Vacuums" |
| Description | `tv_tip` | [0,416][320,476] | "Add a robot vacuum and clean whenever, wherever..." |
| Add Button | `tv_add_device` | [37,528][283,572] | "Add Robot Vacuum" |

### Bottom Navigation Bar
| Tab | Resource ID | Bounds | Selected |
|-----|-------------|--------|----------|
| Home | `tab_home` | [0,590][64,640] | No |
| Cameras | `tab_camera` | [64,590][128,640] | No |
| Vacuums | `tab_robot` | [128,590][192,640] | **Yes** |
| Smart | `tab_smart` | [192,590][256,640] | No |
| Me | `tab_me` | [256,590][320,640] | No |

## Interactive Elements Summary

### Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Add Robot Vacuum (header) | `296, 48` | `adb shell input tap 296 48` |
| Add Robot Vacuum (button) | `160, 550` | `adb shell input tap 160 550` |

## Discovered Screens (for queue)
- `add-robot-vacuum` - tap Add Robot Vacuum button

## Notes
- This is an empty state screen (no robot vacuums configured)
- Both header icon and main button lead to the same add device flow

## Navigation Path
`home` -> tap Vacuums in bottom nav -> `vacuums-tab`

## Raw XML Reference
Dumped via: `adb -s emulator-5554 shell uiautomator dump /sdcard/ui.xml`
