# Smart Tab (Automations) Documentation (Worker-1)

**Activity:** `com.tplink.iot/.view.main.MainActivity` (same as home, different tab)
**Screen Resolution:** 320x640
**Documented:** 2026-01-09
**Screenshot:** `screenshots/tapo-smart-tab-automations-schedules-worker1.png`

## Screen Structure

### Header Section
| Element | Resource ID | Bounds | Content-desc | Clickable |
|---------|-------------|--------|--------------|-----------|
| History | `smart_history_action` | [224,24][272,72] | "History" | Yes |
| Add Smart Action | `smart_add_action` | [272,24][320,72] | "Add Smart Action" | Yes |

### Sub-Tab Navigation
**Container:** `smart_tab` (HorizontalScrollView) - bounds [6,72][320,124]

| Tab | Bounds | Selected | Clickable | Content-desc |
|-----|--------|----------|-----------|--------------|
| Recommended | [6,72][153,124] | **Yes** | No | "Recommended" |
| Shortcuts | [153,72][255,124] | No | Yes | "Shortcuts" |
| Automation | [255,72][320,124] | No | Yes | "Automation" |

### Content Area (ViewPager)
**Container:** `smart_view_pager` - bounds [0,128][320,590]
**Scroll View:** `nested_scroll_view` - scrollable

#### Shortcuts Section
**Header:** "Shortcut" (`tv_text1`) - bounds [20,128][300,147] - content-desc "Recommended Shortcuts"

| Element | Resource ID | Bounds | Title | Description |
|---------|-------------|--------|-------|-------------|
| Leave Home | `cv_root` | [16,157][181,423] | "Leave Home" | "Turn off all your Tapo devices with one simple tap." |
| Arrive Home | `cv_root` | [193,157][320,423] | "Arrive Home" | "Turn on all your Tapo devices with one simple tap." |

**Shortcut Card Elements:**
- Image: `iv_shortcut` - top area
- Title: `tv_title` - below image
- Subtitle: `tv_subtitle` - description

#### Automation Section
**Header:** "Automation" (`tv_text2`) - bounds [20,447][300,466] - content-desc "Recommended Automation"

| Element | Resource ID | Bounds | Title | Subtitle |
|---------|-------------|--------|-------|----------|
| Tap to Alarm | `layout_automation_item` | [16,476][304,590] | "Tap to Alarm" | "0 devices available" |

### Bottom Navigation Bar
**Container:** `bv_bottomNavigation` - bounds [0,590][320,640]

| Tab | Resource ID | Bounds | Selected |
|-----|-------------|--------|----------|
| Home | `tab_home` | [0,590][64,640] | No |
| Cameras | `tab_camera` | [64,590][128,640] | No |
| Vacuums | `tab_robot` | [128,590][192,640] | No |
| Smart | `tab_smart` | [192,590][256,640] | **Yes** |
| Me | `tab_me` | [256,590][320,640] | No |

## Interactive Elements Summary

### Header Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| View History | `248, 48` | `adb shell input tap 248 48` |
| Add Smart Action | `296, 48` | `adb shell input tap 296 48` |

### Tab Navigation
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Shortcuts Tab | `204, 98` | `adb shell input tap 204 98` |
| Automation Tab | `287, 98` | `adb shell input tap 287 98` |

### Shortcut Cards
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Leave Home Shortcut | `98, 290` | `adb shell input tap 98 290` |
| Arrive Home Shortcut | `256, 290` | `adb shell input tap 256 290` |

### Automation Cards
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Tap to Alarm | `160, 533` | `adb shell input tap 160 533` |

## Discovered Screens (for queue)
- `smart-history` - tap History button
- `create-smart-action` - tap Add Smart Action
- `shortcuts-tab` - tap Shortcuts sub-tab
- `automation-tab` - tap Automation sub-tab
- `leave-home-shortcut-setup` - tap Leave Home card
- `arrive-home-shortcut-setup` - tap Arrive Home card
- `tap-to-alarm-setup` - tap Tap to Alarm automation

## Navigation Path
`home` -> tap Smart in bottom nav -> `smart-tab`

## Raw XML Reference
Dumped via: `adb -s emulator-5554 shell uiautomator dump /sdcard/ui.xml`
