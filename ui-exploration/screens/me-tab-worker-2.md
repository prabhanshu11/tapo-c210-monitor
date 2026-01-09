# Me Tab Screen - Worker 2 Documentation

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T06:52:00Z
**Package:** com.tplink.iot

## Screen Overview
The Me/Profile tab in the Tapo app. Shows user account info, Tapo Care subscription, device management options, and app settings.

## UI Structure

### User Profile Header (bounds: [0,92][320,175])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Profile Card | `cv_head_info` | Button | - | "mail.prabhanshu, m a i l . p r a b h a n s h u @ g m a i l . c o m , View Account" | [0,92][320,175] | Yes |
| User Avatar | `tcv_user_head` | ImageView | - | - | [20,97][92,169] | No |
| Username | `tv_user_name` | TextView | "mail.prabhanshu" | - | [108,92][288,125] | No |
| Email | `tv_user_account` | TextView | "mail.prabhanshu@gmail.com" | - | [108,129][292,148] | No |
| View Account | `tv_me_view_account` | TextView | "View Account" | - | [108,156][193,175] | No |

### Tapo Care Section (bounds: [16,191][304,281])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Tapo Care Card | `rl_tapo_care` | Button | - | "Tapo Care Subscribe now to enjoy unlimited cloud storage" | [16,191][304,281] | Yes |
| Title | `tv_title` | TextView | "Tapo Care" | - | [80,207][254,230] | No |
| Subtitle | `tv_bottom_info` | TextView | "Subscribe now to enjoy unlimited cloud storage" | - | [80,230][270,265] | No |

### Devices Section (bounds: [16,326][304,438])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Section Header | `tv_device_header` | TextView | "Devices" | - | [20,297][300,316] | No |
| Playback & Download | `tv_playback_download` | Button | "Playback & Download" | "Playback & Download" | [16,326][304,382] | Yes |
| Camera Memory | `tv_camera_memory` | Button | "Camera Memory" | "Camera Memory" | [16,382][304,438] | Yes |

### Settings Section (bounds: [16,454][304,590])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Firmware Update | `rl_firmware` | Button | "Firmware Update" | "Firmware Update" | [16,454][304,510] | Yes |
| Notifications | `tv_notification` | Button | "Notifications" | "Notifications" | [16,510][304,566] | Yes |
| Device Sharing | `tv_device_share` | Button | "Device Sharing" | "Device Sharing" | [16,566][304,590+] | Yes |

### Bottom Navigation (bounds: [0,590][320,640])
Same structure as home screen. "Me" tab is selected.

## Navigation Paths

### From this screen:
- **Tap Profile Card** -> `account-details` (user profile/settings)
- **Tap Tapo Care** -> `tapo-care-subscription` (cloud storage plans)
- **Tap Playback & Download** -> `playback-download` (recorded videos)
- **Tap Camera Memory** -> `camera-memory` (SD card management)
- **Tap Firmware Update** -> `firmware-update` (device updates)
- **Tap Notifications** -> `notifications-settings` (push notification settings)
- **Tap Device Sharing** -> `device-sharing` (share access with family)
- **Scroll down** -> More settings options (App Settings, Help & Feedback, etc.)

## Discovered Screens
- `account-details` - Tap profile card [0,92][320,175]
- `tapo-care-subscription` - Tap Tapo Care [16,191][304,281]
- `playback-download` - Tap Playback & Download [16,326][304,382]
- `camera-memory` - Tap Camera Memory [16,382][304,438]
- `firmware-update` - Tap Firmware Update [16,454][304,510]
- `notifications-settings` - Tap Notifications [16,510][304,566]
- `device-sharing` - Tap Device Sharing [16,566][304,590]

## Key Resource IDs
- `root_scroll_view` - Main scrollable container
- `ll_main_content` - Main content linear layout
- `cv_head_info` - Profile card container
- `cv_cloud_service` - Tapo Care section container
- `rl_tapo_care` - Tapo Care button

## Notes
- Screen is scrollable (more options below visible area)
- Email is fully displayed: mail.prabhanshu@gmail.com
- Me tab shows "New features" in content-desc (badge indicator)
- This screen doesn't require camera access (no ANR issues)
