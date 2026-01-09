# Me Tab (Profile/Settings) Screen (CONSENSUS)

**Activity:** `com.tplink.iot/.view.main.MainActivity` (same as home, different tab)
**Screen Resolution:** 320x640
**Confirmed by:** Worker-1, Worker-2
**Consensus reached:** 2026-01-09

## Screen Structure

### User Profile Header [0,92][320,175]
| Element | Resource ID | Bounds | Text | Confirmed |
|---------|-------------|--------|------|-----------|
| Profile Card | `cv_head_info` | [0,92][320,175] | - | ✅ Both |
| User Avatar | `tcv_user_head` | [20,97][92,169] | - | ✅ Both |
| Username | `tv_user_name` | [108,92][288,125] | "mail.prabhanshu" | ✅ Both |
| Email | `tv_user_account` | [108,129][292,148] | "mail.prabhanshu@gmail.com" | ✅ Both |
| View Account | `tv_me_view_account` | [108,156][193,175] | "View Account" | ✅ Both |

### Tapo Care Section [16,191][304,281]
| Element | Resource ID | Bounds | Text | Confirmed |
|---------|-------------|--------|------|-----------|
| Tapo Care Card | `rl_tapo_care` | [16,191][304,281] | - | ✅ Both |
| Title | `tv_title` | [80,207][254,230] | "Tapo Care" | ✅ Both |
| Subtitle | `tv_bottom_info` | [80,230][270,265] | "Subscribe now to enjoy..." | ✅ Both |
| Icon | `image_item` | [36,222][64,250] | - | ✅ W1 |
| Arrow | `arrow_more` | [276,224][288,248] | - | ✅ W1 |

### Devices Section [16,326][304,438]
| Element | Resource ID | Bounds | Content-desc | Confirmed |
|---------|-------------|--------|--------------|-----------|
| Section Header | `tv_device_header` | [20,297][300,316] | "Devices" | ✅ Both |
| Playback & Download | `tv_playback_download` | [16,326][304,382] | "Playback & Download" | ✅ Both |
| Camera Memory | `tv_camera_memory` | [16,382][304,438] | "Camera Memory" | ✅ Both |

### Settings Section [16,454][304,590]
| Element | Resource ID | Bounds | Content-desc | Confirmed |
|---------|-------------|--------|--------------|-----------|
| Firmware Update | `rl_firmware` | [16,454][304,510] | "Firmware Update" | ✅ Both |
| Notifications | `tv_notification` | [16,510][304,566] | "Notifications" | ✅ Both |
| Device Sharing | `tv_device_share` | [16,566][304,590+] | "Device Sharing" | ✅ Both |

### Bottom Navigation [0,590][320,640]
**Container:** `bv_bottomNavigation`
- Me tab is **selected**

## Navigation Actions (VERIFIED)

### Account Actions
| Action | Tap Coordinates | ADB Command | Confirmed |
|--------|-----------------|-------------|-----------|
| View Account/Profile | `160, 133` | `adb shell input tap 160 133` | ✅ Both |

### Subscription Actions
| Action | Tap Coordinates | ADB Command | Confirmed |
|--------|-----------------|-------------|-----------|
| Tapo Care Subscription | `160, 236` | `adb shell input tap 160 236` | ✅ Both |

### Device Management Actions
| Action | Tap Coordinates | ADB Command | Confirmed |
|--------|-----------------|-------------|-----------|
| Playback & Download | `160, 354` | `adb shell input tap 160 354` | ✅ Both |
| Camera Memory | `160, 410` | `adb shell input tap 160 410` | ✅ Both |

### Settings Actions
| Action | Tap Coordinates | ADB Command | Confirmed |
|--------|-----------------|-------------|-----------|
| Firmware Update | `160, 482` | `adb shell input tap 160 482` | ✅ Both |
| Notifications Settings | `160, 538` | `adb shell input tap 160 538` | ✅ Both |
| Device Sharing | `160, 578` | `adb shell input tap 160 578` | ✅ Both |

## Discovered Screens
- `account-profile` / `account-details` - tap profile section
- `tapo-care-subscription` - tap Tapo Care
- `playback-download` / `playback-library` - tap Playback & Download
- `camera-memory` / `camera-memory-management` - tap Camera Memory
- `firmware-update` - tap Firmware Update
- `notifications-settings` / `notification-settings` - tap Notifications
- `device-sharing` - tap Device Sharing
- More options available by scrolling

## Key Resource IDs
- `root_scroll_view` - Main scrollable container
- `ll_main_content` - Main content layout
- `cv_head_info` - Profile card container
- `cv_cloud_service` - Tapo Care section
- `rl_tapo_care` - Tapo Care button

## Navigation Path
`home` -> tap Me in bottom nav [288,615] -> `me-tab`

## Notes
- Screen is scrollable (more options below visible area)
- No camera access required - stable, no ANR issues
- "New features" badge visible on Me tab indicator
