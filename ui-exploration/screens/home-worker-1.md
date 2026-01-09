# Home Screen Documentation (Worker-1)

**Activity:** `com.tplink.iot/.view.main.MainActivity`
**Screen Resolution:** 320x640
**Documented:** 2026-01-09

## Screen Structure

### Header Section (Top Bar)
| Element | Resource ID | Bounds | Content-desc | Clickable | Notes |
|---------|-------------|--------|--------------|-----------|-------|
| Family Selector | `cl_family_name_toolbar` | [8,24][214,72] | "Home, My home" | Yes | Shows "My home" text, has dropdown arrow |
| Home Name Text | `tv_family_name_toolbar` | [8,24][83,72] | - | Yes | Text: "My home" |
| Dropdown Arrow | `iv_family_switch_toolbar` | [87,40][103,56] | - | No | Part of family selector |
| Notifications | `iv_home_menu_message` | [224,24][272,72] | "Notifications" | Yes | ImageButton |
| Add Device | `iv_home_menu_add` | [272,24][320,72] | "Add Device or Add Group" | Yes | ImageButton |

### Tab Section (Room/Category Filter)
| Element | Bounds | Content-desc | Selected | Clickable |
|---------|--------|--------------|----------|-----------|
| Favorites Tab | [6,112][113,142] | "Favorites" | Yes | No (already selected) |
| All Devices Tab | [113,112][227,142] | "All Devices" | No | Yes |
| Bedroom Tab | [227,112][268,142] | "Bedroom" | No | Yes |
| More Rooms | [268,103][316,151] | "More" | - | Yes |

**Tab Layout Container:** `tab_layout` - HorizontalScrollView with scrollable tabs

### Device Grid (Content Area)
**Container:** `content_view_pager` (ViewPager) - bounds [0,142][320,590]
**Grid:** `recycler_view` (GridView) - bounds [0,142][320,590]

#### Device Card: Tapo_C210_69A3
| Element | Resource ID | Bounds | Value/Desc |
|---------|-------------|--------|------------|
| Card Container | `content` | [16,160][154,280] | Button, long-clickable |
| Device Image | `iv_device_image` | [28,170][68,210] | Camera icon |
| Privacy Toggle | `device_switch` | [106,160][154,208] | ImageView, clickable |
| Device Name | `tv_device_name` | [32,230][138,249] | "Tapo_C210_69A3" |
| Location | `tv_location` | [32,253][83,268] | "Bedroom" |

**Card Content-desc:** "Tapo_C210_69A3,Bedroom,Privacy Mode is Off"

### Bottom Navigation Bar
**Container:** `bv_bottomNavigation` - bounds [0,590][320,640]

| Tab | Resource ID | Bounds | Selected | Content-desc |
|-----|-------------|--------|----------|--------------|
| Home | `tab_home` | [0,590][64,640] | Yes | "Home" |
| Cameras | `tab_camera` | [64,590][128,640] | No | "Cameras" |
| Vacuums | `tab_robot` | [128,590][192,640] | No | "Vacuums" |
| Smart | `tab_smart` | [192,590][256,640] | No | "Smart" |
| Me | `tab_me` | [256,590][320,640] | No | "New features" |

## Interactive Elements Summary

### Primary Actions
1. **Tap Device Card** [16,160][154,280] - Opens camera live view (discovered screen: `camera-live`)
2. **Toggle Privacy** [106,160][154,208] - Toggles camera privacy mode
3. **Long-press Device Card** - Opens device options menu (discovered screen: `device-options`)

### Navigation Actions
1. **Notifications** [224,24][272,72] - Opens notifications (discovered screen: `notifications`)
2. **Add Device** [272,24][320,72] - Opens add device flow (discovered screen: `add-device`)
3. **Family Selector** [8,24][214,72] - Opens home/family picker (discovered screen: `family-picker`)
4. **More Rooms** [268,103][316,151] - Opens room management (discovered screen: `room-management`)

### Bottom Nav Actions
1. **Cameras Tab** [64,590][128,640] - Opens cameras grid (discovered screen: `cameras-tab`)
2. **Vacuums Tab** [128,590][192,640] - Opens vacuums view (discovered screen: `vacuums-tab`)
3. **Smart Tab** [192,590][256,640] - Opens smart/automation (discovered screen: `smart-tab`)
4. **Me Tab** [256,590][320,640] - Opens profile/settings (discovered screen: `me-tab`)

## Discovered Screens (for queue)
- `camera-live` - tap camera card
- `device-options` - long-press camera card
- `notifications` - tap notification bell
- `add-device` - tap + button
- `family-picker` - tap "My home" selector
- `room-management` - tap "More" in tabs
- `cameras-tab` - tap Cameras in bottom nav
- `vacuums-tab` - tap Vacuums in bottom nav
- `smart-tab` - tap Smart in bottom nav
- `me-tab` - tap Me in bottom nav

## Navigation Path
Entry point after login - this is the main dashboard.

## Raw XML Reference
Dumped via: `adb -s emulator-5554 shell uiautomator dump /sdcard/ui.xml`
