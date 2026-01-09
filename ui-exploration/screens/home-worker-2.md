# Home Screen - Worker 2 Documentation

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T06:45:00Z
**Package:** com.tplink.iot

## Screen Overview
The main home screen of the Tapo app. Shows a header with home selector, device tabs, a grid of device cards, and bottom navigation.

## UI Structure

### Header (bounds: [0,0][320,72])

| Element | Resource ID | Type | Content-Desc | Bounds | Clickable |
|---------|-------------|------|--------------|--------|-----------|
| Home Selector | `cl_family_name_toolbar` | Button | "Home, My home" | [8,24][214,72] | Yes |
| Home Name | `tv_family_name_toolbar` | TextView | - | [8,24][83,72] | Yes |
| Dropdown Arrow | `iv_family_switch_toolbar` | ImageView | - | [87,40][103,56] | No |
| Notifications | `iv_home_menu_message` | ImageButton | "Notifications" | [224,24][272,72] | Yes |
| Add Device | `iv_home_menu_add` | ImageButton | "Add Device or Add Group" | [272,24][320,72] | Yes |

### Tab Layout (bounds: [6,112][268,142])

| Tab | Text | Content-Desc | Bounds | Selected |
|-----|------|--------------|--------|----------|
| Favorites | "Favorites" | "Favorites" | [6,112][113,142] | Yes |
| All Devices | "All Devices" | "All Devices" | [113,112][227,142] | No |
| Bedroom | "Bedroom" | "Bedroom" | [227,112][268,142] | No |

| Element | Resource ID | Type | Content-Desc | Bounds | Clickable |
|---------|-------------|------|--------------|--------|-----------|
| More Rooms | `room_all_navigation` | Button | "More" | [268,103][316,151] | Yes |

### Device Grid (bounds: [0,142][320,590])

| Element | Resource ID | Type | Content-Desc | Bounds | Clickable | Long-Clickable |
|---------|-------------|------|--------------|--------|-----------|----------------|
| Camera Card | `content` | Button | "Tapo_C210_69A3,Bedroom,Privacy Mode is Off" | [16,160][154,280] | Yes | Yes |
| Device Image | `iv_device_image` | ImageView | - | [28,170][68,210] | No | No |
| Privacy Toggle | `device_switch` | ImageView | - | [106,160][154,208] | Yes | No |
| Device Name | `tv_device_name` | TextView | "Tapo_C210_69A3" | [32,230][138,249] | No | No |
| Device Location | `tv_location` | TextView | "Bedroom" | [32,253][83,268] | No | No |

### Bottom Navigation (bounds: [0,590][320,640])

| Tab | Resource ID | Text | Content-Desc | Bounds | Selected |
|-----|-------------|------|--------------|--------|----------|
| Home | `tab_home` | "Home" | "Home" | [0,590][64,640] | Yes |
| Cameras | `tab_camera` | "Cameras" | "Cameras" | [64,590][128,640] | No |
| Vacuums | `tab_robot` | "Vacuums" | "Vacuums" | [128,590][192,640] | No |
| Smart | `tab_smart` | "Smart" | "Smart" | [192,590][256,640] | No |
| Me | `tab_me` | "Me" | "New features" | [256,590][320,640] | No |

## Navigation Paths

### From this screen:
- **Tap Camera Card** -> `camera-live` (live view)
- **Long-press Camera Card** -> Device options menu
- **Tap Privacy Toggle** -> Toggle privacy mode
- **Tap Notifications** -> Notifications screen
- **Tap Add Device** -> Add device flow
- **Tap Home Selector** -> Home switching menu
- **Tap More** -> Room management
- **Tap Cameras tab** -> Cameras tab view
- **Tap Vacuums tab** -> Vacuums tab view
- **Tap Smart tab** -> Smart automations
- **Tap Me tab** -> User profile/settings

## Discovered Screens
- `camera-live` - Tap on camera card [16,160][154,280]
- `notifications` - Tap notifications button [224,24][272,72]
- `add-device` - Tap add button [272,24][320,72]
- `home-selector` - Tap home selector [8,24][214,72]
- `room-management` - Tap more button [268,103][316,151]
- `cameras-tab` - Tap cameras nav [64,590][128,640]
- `vacuums-tab` - Tap vacuums nav [128,590][192,640]
- `smart-tab` - Tap smart nav [192,590][256,640]
- `me-tab` - Tap me nav [256,590][320,640]

## Key Resource IDs
- `srv_home_list` - Main scrollable home container
- `view_scroll` - ScrollView containing content
- `tab_layout` - HorizontalScrollView for device tabs
- `content_view_pager` - ViewPager for tab content
- `recycler_view` - GridView for device cards
- `bv_bottomNavigation` - Bottom navigation container

## Notes
- Screen resolution: 320x640 (small emulator display)
- Device shows privacy mode status in content-desc
- Long-click on device card available for additional options
