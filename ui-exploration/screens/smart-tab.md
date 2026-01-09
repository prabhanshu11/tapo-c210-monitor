# Smart Tab (Automations) Screen (CONSENSUS)

**Activity:** `com.tplink.iot/.view.main.MainActivity` (same as home, different tab)
**Screen Resolution:** 320x640
**Confirmed by:** Worker-1, Worker-2
**Consensus reached:** 2026-01-09

## Screen Structure

### Header Section [0,24][320,72]
| Element | Resource ID | Bounds | Content-desc | Confirmed |
|---------|-------------|--------|--------------|-----------|
| History | `smart_history_action` | [224,24][272,72] | "History" | ✅ Both |
| Add Smart Action | `smart_add_action` | [272,24][320,72] | "Add Smart Action" | ✅ Both |

### Sub-Tab Navigation [6,72][320,124]
**Container:** `smart_tab` (HorizontalScrollView)

| Tab | Bounds | Selected | Clickable | Confirmed |
|-----|--------|----------|-----------|-----------|
| Recommended | [6,72][153,124] | **Yes** | No | ✅ Both |
| Shortcuts | [153,72][255,124] | No | Yes | ✅ Both |
| Automation | [255,72][320,124] | No | Yes | ✅ Both |

### Shortcut Section [0,157][320,447]
**Header:** "Shortcut" (`tv_text1`) - "Recommended Shortcuts"

| Element | Resource ID | Bounds | Title | Description | Confirmed |
|---------|-------------|--------|-------|-------------|-----------|
| Leave Home | `cv_root` | [16,157][181,423] | "Leave Home" | "Turn off all your Tapo devices..." | ✅ Both |
| Arrive Home | `cv_root` | [193,157][320,423] | "Arrive Home" | "Turn on all your Tapo devices..." | ✅ Both |

### Automation Section [0,447][320,590]
**Header:** "Automation" (`tv_text2`) - "Recommended Automation"

| Element | Resource ID | Bounds | Title | Subtitle | Confirmed |
|---------|-------------|--------|-------|----------|-----------|
| Tap to Alarm | `layout_automation_item` | [16,476][304,590] | "Tap to Alarm" | "0 devices available" | ✅ Both |

### Bottom Navigation [0,590][320,640]
**Container:** `bv_bottomNavigation`
- Smart tab is **selected**

## Navigation Actions (VERIFIED)

### Header Actions
| Action | Tap Coordinates | ADB Command | Confirmed |
|--------|-----------------|-------------|-----------|
| View History | `248, 48` | `adb shell input tap 248 48` | ✅ Both |
| Add Smart Action | `296, 48` | `adb shell input tap 296 48` | ✅ Both |

### Tab Navigation
| Action | Tap Coordinates | ADB Command | Confirmed |
|--------|-----------------|-------------|-----------|
| Shortcuts Tab | `204, 98` | `adb shell input tap 204 98` | ✅ Both |
| Automation Tab | `287, 98` | `adb shell input tap 287 98` | ✅ Both |

### Shortcut Cards
| Action | Tap Coordinates | ADB Command | Confirmed |
|--------|-----------------|-------------|-----------|
| Leave Home Shortcut | `98, 290` | `adb shell input tap 98 290` | ✅ Both |
| Arrive Home Shortcut | `256, 290` | `adb shell input tap 256 290` | ✅ Both |

### Automation Cards
| Action | Tap Coordinates | ADB Command | Confirmed |
|--------|-----------------|-------------|-----------|
| Tap to Alarm | `160, 533` | `adb shell input tap 160 533` | ✅ Both |

## Discovered Screens
- `smart-history` - tap History button
- `add-smart-action` / `create-smart-action` - tap Add Smart Action
- `shortcuts-tab` - tap Shortcuts sub-tab
- `automation-tab` - tap Automation sub-tab
- `leave-home-shortcut-setup` / `shortcut-leave-home` - tap Leave Home card
- `arrive-home-shortcut-setup` / `shortcut-arrive-home` - tap Arrive Home card
- `tap-to-alarm-setup` / `automation-tap-alarm` - tap Tap to Alarm

## Key Resource IDs
- `smart_header` - Header container
- `smart_tab` - Tab layout (HorizontalScrollView)
- `smart_view_pager` - Content ViewPager
- `rv_shortcut` - Shortcuts RecyclerView
- `rv_automation` - Automation RecyclerView
- `refresh_layout` - Pull-to-refresh container
- `nested_scroll_view` - Scrollable content

## Shortcut Card Structure
- `iv_shortcut` - Illustration image
- `ll_shortcut` - Text container
- `tv_title` - Shortcut name
- `tv_subtitle` - Shortcut description

## Navigation Path
`home` -> tap Smart in bottom nav [224,615] -> `smart-tab`

## Notes
- Screen shows recommended templates on first load
- No camera access needed - stable screen
- Shortcuts allow one-tap actions (Leave Home, Arrive Home)
- Automations allow trigger-based actions
- "0 devices available" indicates no compatible devices for that automation
