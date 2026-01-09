# Me Tab (Profile/Settings) Documentation (Worker-1)

**Activity:** `com.tplink.iot/.view.main.MainActivity` (same as home, different tab)
**Screen Resolution:** 320x640
**Documented:** 2026-01-09
**Screenshot:** `screenshots/tapo-me-tab-profile-settings-account-worker1.png`

## Screen Structure

### Profile Section
**Container:** `cv_head_info` - bounds [0,92][320,175] - clickable

| Element | Resource ID | Bounds | Text | Notes |
|---------|-------------|--------|------|-------|
| Profile Container | `cv_head_info` | [0,92][320,175] | - | content-desc: "mail.prabhanshu, m a i l . p r a b h a n s h u @ g m a i l . c o m, View Account" |
| User Avatar | `tcv_user_head` | [20,97][92,169] | - | Profile image |
| Username | `tv_user_name` | [108,92][288,125] | "mail.prabhanshu" | Display name |
| Email | `tv_user_account` | [108,129][292,148] | "mail.prabhanshu@gmail.com" | Account email |
| View Account | `tv_me_view_account` | [108,156][193,175] | "View Account" | Link text |

### Tapo Care Promotion
**Container:** `cv_cloud_service` - bounds [16,191][304,281]

| Element | Resource ID | Bounds | Text | Clickable |
|---------|-------------|--------|------|-----------|
| Tapo Care Button | `rl_tapo_care` | [16,191][304,281] | - | Yes |
| Title | `tv_title` | [80,207][254,230] | "Tapo Care" | No |
| Subtitle | `tv_bottom_info` | [80,230][270,265] | "Subscribe now to enjoy unlimited cloud storage" | No |
| Icon | `image_item` | [36,222][64,250] | - | No |
| Arrow | `arrow_more` | [276,224][288,248] | - | No |

### Devices Section
**Header:** "Devices" (`tv_device_header`) - bounds [20,297][300,316]

| Element | Resource ID | Bounds | Content-desc | Clickable |
|---------|-------------|--------|--------------|-----------|
| Playback & Download | `tv_playback_download` | [16,326][304,382] | "Playback & Download" | Yes |
| Camera Memory | `tv_camera_memory` | [16,382][304,438] | "Camera Memory" | Yes |

### Settings Section

| Element | Resource ID | Bounds | Content-desc | Clickable |
|---------|-------------|--------|--------------|-----------|
| Firmware Update | `rl_firmware` | [16,454][304,510] | "Firmware Update" | Yes |
| Notifications | `tv_notification` | [16,510][304,566] | "Notifications" | Yes |
| Device Sharing | `tv_device_share` | [16,566][304,590] | "Device Sharing" | Yes (partially visible) |

### Bottom Navigation Bar
**Container:** `bv_bottomNavigation` - bounds [0,590][320,640]

| Tab | Resource ID | Bounds | Selected |
|-----|-------------|--------|----------|
| Home | `tab_home` | [0,590][64,640] | No |
| Cameras | `tab_camera` | [64,590][128,640] | No |
| Vacuums | `tab_robot` | [128,590][192,640] | No |
| Smart | `tab_smart` | [192,590][256,640] | No |
| Me | `tab_me` | [256,590][320,640] | **Yes** |

## Interactive Elements Summary

### Account Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| View Account/Profile | `160, 133` | `adb shell input tap 160 133` |

### Subscription Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Tapo Care Subscription | `160, 236` | `adb shell input tap 160 236` |

### Device Management Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Playback & Download | `160, 354` | `adb shell input tap 160 354` |
| Camera Memory | `160, 410` | `adb shell input tap 160 410` |

### Settings Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Firmware Update | `160, 482` | `adb shell input tap 160 482` |
| Notifications Settings | `160, 538` | `adb shell input tap 160 538` |
| Device Sharing | `160, 578` | `adb shell input tap 160 578` |

## Discovered Screens (for queue)
- `account-profile` - tap profile section (view/edit account)
- `tapo-care-subscription` - tap Tapo Care
- `playback-library` - tap Playback & Download
- `camera-memory-management` - tap Camera Memory
- `firmware-update` - tap Firmware Update
- `notification-settings` - tap Notifications
- `device-sharing` - tap Device Sharing

## Scrollable Content
The screen uses `root_scroll_view` - there may be more menu items below the visible area that require scrolling to access.

## Navigation Path
`home` -> tap Me in bottom nav -> `me-tab`

## Raw XML Reference
Dumped via: `adb -s emulator-5554 shell uiautomator dump /sdcard/ui.xml`
