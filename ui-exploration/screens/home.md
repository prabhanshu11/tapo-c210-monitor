# Home Screen (CONSENSUS)

**Activity:** `com.tplink.iot/.view.main.MainActivity`
**Screen Resolution:** 320x640
**Confirmed by:** Worker-1, Worker-2
**Consensus reached:** 2026-01-09

## Screen Structure

### Header Section [0,0][320,72]
| Element | Resource ID | Bounds | Content-desc | Clickable | Confirmed |
|---------|-------------|--------|--------------|-----------|-----------|
| Family Selector | `cl_family_name_toolbar` | [8,24][214,72] | "Home, My home" | Yes | ✅ Both |
| Home Name Text | `tv_family_name_toolbar` | [8,24][83,72] | - | Yes | ✅ Both |
| Dropdown Arrow | `iv_family_switch_toolbar` | [87,40][103,56] | - | No | ✅ Both |
| Notifications | `iv_home_menu_message` | [224,24][272,72] | "Notifications" | Yes | ✅ Both |
| Add Device | `iv_home_menu_add` | [272,24][320,72] | "Add Device or Add Group" | Yes | ✅ Both |

### Tab Section [6,112][268,142]
| Tab | Bounds | Content-desc | Selected | Confirmed |
|-----|--------|--------------|----------|-----------|
| Favorites | [6,112][113,142] | "Favorites" | Yes | ✅ Both |
| All Devices | [113,112][227,142] | "All Devices" | No | ✅ Both |
| Bedroom | [227,112][268,142] | "Bedroom" | No | ✅ Both |
| More Rooms | [268,103][316,151] | "More" | - | ✅ Both |

**Tab Container:** `tab_layout` - HorizontalScrollView

### Device Grid [0,142][320,590]
**Container:** `content_view_pager` (ViewPager)
**Grid:** `recycler_view` (GridView)

#### Device Card: Tapo_C210_69A3
| Element | Resource ID | Bounds | Value | Confirmed |
|---------|-------------|--------|-------|-----------|
| Card Container | `content` | [16,160][154,280] | Button, long-clickable | ✅ Both |
| Device Image | `iv_device_image` | [28,170][68,210] | Camera icon | ✅ Both |
| Privacy Toggle | `device_switch` | [106,160][154,208] | Clickable ImageView | ✅ Both |
| Device Name | `tv_device_name` | [32,230][138,249] | "Tapo_C210_69A3" | ✅ Both |
| Location | `tv_location` | [32,253][83,268] | "Bedroom" | ✅ Both |

**Card Content-desc:** "Tapo_C210_69A3,Bedroom,Privacy Mode is Off"

### Bottom Navigation [0,590][320,640]
**Container:** `bv_bottomNavigation`

| Tab | Resource ID | Bounds | Selected | Confirmed |
|-----|-------------|--------|----------|-----------|
| Home | `tab_home` | [0,590][64,640] | Yes | ✅ Both |
| Cameras | `tab_camera` | [64,590][128,640] | No | ✅ Both |
| Vacuums | `tab_robot` | [128,590][192,640] | No | ✅ Both |
| Smart | `tab_smart` | [192,590][256,640] | No | ✅ Both |
| Me | `tab_me` | [256,590][320,640] | No | ✅ Both |

## Navigation Actions (VERIFIED)

### Primary Actions
| Action | Bounds | Target Screen | Confirmed |
|--------|--------|---------------|-----------|
| Tap Device Card | [16,160][154,280] | `camera-live` | ✅ Both |
| Toggle Privacy | [106,160][154,208] | Privacy toggle | ✅ Both |
| Long-press Card | [16,160][154,280] | `device-options` | ✅ W1 only |

### Header Actions
| Action | Bounds | Target Screen | Confirmed |
|--------|--------|---------------|-----------|
| Tap Notifications | [224,24][272,72] | `notifications` | ✅ Both |
| Tap Add Device | [272,24][320,72] | `add-device` | ✅ Both |
| Tap Family Selector | [8,24][214,72] | `family-picker` | ✅ Both |
| Tap More Rooms | [268,103][316,151] | `room-management` | ✅ Both |

### Bottom Nav Actions
| Action | Bounds | Target Screen | Confirmed |
|--------|--------|---------------|-----------|
| Tap Cameras | [64,590][128,640] | `cameras-tab` | ✅ Both |
| Tap Vacuums | [128,590][192,640] | `vacuums-tab` | ✅ Both |
| Tap Smart | [192,590][256,640] | `smart-tab` | ✅ Both |
| Tap Me | [256,590][320,640] | `me-tab` | ✅ Both |

## Key Resource IDs
- `srv_home_list` - Main scrollable container
- `view_scroll` - ScrollView
- `tab_layout` - Room/category tabs
- `content_view_pager` - ViewPager for tab content
- `recycler_view` - Device card grid
- `bv_bottomNavigation` - Bottom nav bar

## Notes
- Entry point after login - main dashboard
- Privacy mode status shown in card content-desc
- Long-click on device card opens options menu
