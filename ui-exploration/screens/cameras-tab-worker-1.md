# Cameras Tab Documentation (Worker-1)

**Activity:** `com.tplink.iot/.view.main.MainActivity` (same as home, different tab)
**Screen Resolution:** 320x640
**Documented:** 2026-01-09

## Screen Structure

### Header Section
| Element | Resource ID | Bounds | Content-desc | Clickable | Notes |
|---------|-------------|--------|--------------|-----------|-------|
| Add Camera | `camera_add_device` | [272,24][320,72] | "Add Camera" | Yes | Button to add new camera |

### Sub-Tab Navigation
**Container:** `camera_cloud_activity_tab` (HorizontalScrollView) - bounds [20,72][252,120]

| Tab | Bounds | Selected | Clickable | Content-desc |
|-----|--------|----------|-----------|--------------|
| Cameras | [20,72][120,120] | Yes | No (selected) | "Cameras" |
| Cloud Activity | [120,72][252,120] | No | Yes | "Cloud Activity" |

### Content Area (ViewPager)
**Container:** `camera_viewpager` - bounds [0,120][320,590]
**Scroll View:** `scroll_view` - bounds [0,120][320,590] - scrollable

#### Tapo Care Banner
**Container:** `ll_preview_cloud_video_server` - bounds [16,136][304,352]

| Element | Resource ID | Bounds | Text/Content | Clickable |
|---------|-------------|--------|--------------|-----------|
| Banner (full) | `ll_preview_cloud_video_server` | [16,136][304,352] | "Tapo Care Cloud Storage, Enjoy up to 30 days..." | Yes |
| Title | `tv_cloud_service_title` | [32,152][173,193] | "Tapo Care Cloud Storage" | No |
| Description | `tv_cloud_service_content` | [32,201][173,284] | "Enjoy up to 30 days of cloud video history..." | No |
| Upgrade CTA | `tv_cloud_service_more` | [32,304][165,336] | "Upgrade Now" | No (parent clickable) |
| Background Image | `iv_background_image` | [53,136][304,352] | - | No |
| Close Banner | `iv_cloud_service_close` | [256,136][304,184] | "Close" | Yes |

#### Detection Mode Section
**Container:** `camera_preview_mode_part` - bounds [16,352][304,560]

| Element | Resource ID | Bounds | Text | Notes |
|---------|-------------|--------|------|-------|
| Section Title | `tv_detection_mode` | [20,366][121,385] | "Detection Mode" | - |
| Home Mode Button | `item_home_mode` | [16,395][153,483] | "Home Mode" | Selectable mode |
| Home Mode Settings | `iv_home_mode_more` | [105,395][153,443] | "Home Mode Settings" | Settings gear |
| Away Mode Button | `item_away_mode` | [166,395][304,483] | "Away Mode" | Selectable mode |
| Away Mode Settings | `iv_away_mode_more` | [256,395][304,443] | "Away Mode Settings" | Settings gear |
| Tip Text | `tv_detection_mode_tip` | [20,493][300,544] | "Tap to activate Home or Away Mode..." | Explanatory text |

#### Devices List Header
| Element | Resource ID | Bounds | Text |
|---------|-------------|--------|------|
| Devices Count | `tv_title` | [20,574][300,590] | "Devices (1)" |

*Note: Device list items are below visible area, need scroll to see*

### Bottom Navigation Bar
**Container:** `bv_bottomNavigation` - bounds [0,590][320,640]

| Tab | Resource ID | Bounds | Selected | Content-desc |
|-----|-------------|--------|----------|--------------|
| Home | `tab_home` | [0,590][64,640] | No | "Home" |
| Cameras | `tab_camera` | [64,590][128,640] | **Yes** | "Cameras" |
| Vacuums | `tab_robot` | [128,590][192,640] | No | "Vacuums" |
| Smart | `tab_smart` | [192,590][256,640] | No | "Smart" |
| Me | `tab_me` | [256,590][320,640] | No | "New features" |

## Interactive Elements Summary

### Primary Actions
1. **Add Camera** [272,24][320,72] - Opens add camera flow
2. **Home Mode** [16,395][153,483] - Activates home detection mode
3. **Away Mode** [166,395][304,483] - Activates away detection mode

### Settings Actions
1. **Home Mode Settings** [105,395][153,443] - Opens home mode configuration (discovered screen: `home-mode-settings`)
2. **Away Mode Settings** [256,395][304,443] - Opens away mode configuration (discovered screen: `away-mode-settings`)

### Tab Navigation
1. **Cloud Activity Tab** [120,72][252,120] - Switch to cloud activity view (discovered screen: `cloud-activity-tab`)

### Banner Actions
1. **Tapo Care Banner** [16,136][304,352] - Opens subscription/upgrade (discovered screen: `tapo-care-upgrade`)
2. **Close Banner** [256,136][304,184] - Dismisses the Tapo Care promotion

### Bottom Nav Actions
Same as home screen - navigate between main sections.

## Discovered Screens (for queue)
- `cloud-activity-tab` - tap Cloud Activity sub-tab
- `home-mode-settings` - tap Home Mode settings icon
- `away-mode-settings` - tap Away Mode settings icon
- `tapo-care-upgrade` - tap Tapo Care banner
- `add-camera-flow` - tap Add Camera button

## Key Differences from Home Screen
1. **Different header**: Has "Add Camera" button instead of "My home" selector
2. **Sub-tabs**: Has Cameras/Cloud Activity tabs
3. **Detection Modes**: Home/Away mode toggle feature
4. **Device list**: Shows "Devices (1)" count - camera-focused view

## Navigation Path
`home` -> tap Cameras in bottom nav -> `cameras-tab`

## Raw XML Reference
Dumped via: `adb -s emulator-5554 shell uiautomator dump /sdcard/ui.xml`
