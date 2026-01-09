# Camera Live Screen - Worker 2 Documentation

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T06:47:00Z
**Package:** com.tplink.iot

## Screen Overview
The live camera view for a Tapo C210 camera. Shows real-time video feed with camera controls, PTZ functions, recording options, and quick access to device settings.

## UI Structure

### Header/Toolbar (bounds: [0,24][320,88])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Back | `btn_back` | Button | - | "Back" | [0,33][48,81] | Yes |
| Title | `title` | TextView | "Tapo_C210_69A3" | - | [92,45][229,68] | No |
| Settings | `action_settings` | ImageView | - | "Device Settings" | [272,33][320,81] | Yes |

### Video Area (bounds: [0,88][320,268])

| Element | Resource ID | Type | Content-Desc | Bounds | Clickable | Long-Clickable |
|---------|-------------|------|--------------|--------|-----------|----------------|
| Video Container | `live_surface_list_view_container` | FrameLayout | - | [0,88][320,268] | No | No |
| Video Surface | `live_surface_view` | FrameLayout | - | [0,88][320,268] | No | No |
| Player Mask | `accessibility_mask_view` | SeekBar | "Camera Live Player, Streaming" | [0,88][320,268] | No | No |
| Touch Mask | `view_touch_mask` | View | - | [0,88][320,268] | No | No |

### Video Bottom Bar (bounds: [0,220][320,268])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Multi-View | `tool_view` | Button | - | "Switch to Multi-View" | [44,220][92,268] | Yes |
| Video Mode | `tv_infrared_mode` | Button | "Auto" | "Video Mode, Auto" | [136,220][184,268] | Yes |
| Fullscreen | `tool_full_screen` | Button | - | "Fullscreen" | [228,220][276,268] | Yes |

### Media Toolbar (bounds: [0,268][320,336])

| Element | Resource ID | Type | Content-Desc | Bounds | Clickable |
|---------|-------------|------|--------------|--------|-----------|
| Take Photo | `tool_pic` | Button | "Take Photo" | [26,278][74,326] | Yes |
| Record Video | `record_container` | Button | "Manual Recording" | [99,278][147,326] | Yes |
| Record Icon | `tool_video` | ImageView | "Record Video" | [99,278][147,326] | Yes |
| Sound | `tool_sound` | Button | "Camera's Microphone Volume" | [173,278][221,326] | Yes |
| Voice Call | `tool_voice_call` | Button | "Voice Call" | [246,278][294,326] | Yes |

### Control Panel - First Row (bounds: [16,350][304,433])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Talk | `talk_tv` | Button | "Talk" | "Talk" | [16,350][112,433] | Yes |
| Pan & Tilt | `control_tv` | Button | "Pan & Tilt" | "Pan and Tilt Controls" | [112,350][208,433] | Yes |
| Alarm | `call_tv` | Button | "Alarm Off" | "Detection Alarm, Off" | [208,350][304,433] | Yes |

### Control Panel - Second Row (bounds: [16,433][304,516])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Privacy Mode | `privacy_tv` | Button | "Privacy Mode" | "Privacy Mode, Off" | [16,433][112,516] | Yes |
| Tapo Care | `alerts_tv` | Button | "Tapo Care" | "Tapo Care" | [112,433][208,516] | Yes |

### Storage Section (bounds: [16,529][304,640])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Playback & Download | `playback_and_download` | Button | "Playback & Download" | "Playback & Download" | [16,545][304,608] | Yes |
| Cloud Storage Promo | `layout_play_storage_server` | Button | "Tapo Care Cloud Storage" | "Tapo Care Cloud Storage, Enjoy up to 30 days..." | [16,624][304,640] | Yes |
| Dismiss Cloud Promo | `iv_cloud_service_close` | ImageView | - | "Dismiss" | [256,624][304,640] | Yes |

## Navigation Paths

### From this screen:
- **Tap Back** -> `home` (return to home screen)
- **Tap Settings** -> `device-settings` (device configuration)
- **Tap Multi-View** -> `multi-view` (multiple camera view)
- **Tap Video Mode** -> Video mode picker (Auto/Day/Night)
- **Tap Fullscreen** -> `camera-fullscreen` (landscape full video)
- **Tap Take Photo** -> Captures screenshot from camera
- **Tap Record** -> Starts/stops manual recording
- **Tap Sound** -> Volume control for camera microphone
- **Tap Voice Call** -> `voice-call` (two-way audio)
- **Tap Talk** -> Push-to-talk interface
- **Tap Pan & Tilt** -> `pan-tilt-controls` (PTZ joystick)
- **Tap Alarm** -> Toggle detection alarm on/off
- **Tap Privacy Mode** -> Toggle privacy mode on/off
- **Tap Tapo Care** -> `tapo-care` (subscription info)
- **Tap Playback & Download** -> `playback-download` (recorded video)
- **Tap Cloud Storage** -> `cloud-storage-promo` (Tapo Care upsell)

## Discovered Screens
- `device-settings` - Tap settings gear [272,33][320,81]
- `multi-view` - Tap multi-view button [44,220][92,268]
- `camera-fullscreen` - Tap fullscreen button [228,220][276,268]
- `voice-call` - Tap voice call button [246,278][294,326]
- `pan-tilt-controls` - Tap Pan & Tilt [112,350][208,433]
- `tapo-care` - Tap Tapo Care button [112,433][208,516]
- `playback-download` - Tap Playback & Download [16,545][304,608]

## Key Resource IDs
- `fl_root` - Root frame layout
- `coordinator_layout` - Main scrollable container
- `video_fragment` - Video player container
- `live_surface_list_view` - GridView for video surfaces
- `pop_bar_in_bottom` - Video overlay controls
- `toolbar_in_bottom` - Media capture toolbar
- `ll_control_panel` - Control buttons panel
- `sv_control_layout` - Scrollable control area
- `fl_cloud_storage_fragment` - Storage/playback section

## States and Toggles
- **Video Mode**: Shows current mode ("Auto" in content-desc)
- **Detection Alarm**: Shows on/off state ("Detection Alarm, Off")
- **Privacy Mode**: Shows on/off state ("Privacy Mode, Off")
- **Camera Status**: Streaming indicator in accessibility_mask_view

## Notes
- Screen resolution: 320x640
- Video area takes top portion (88-336px height)
- Controls are scrollable below video
- Long-press on video surface available
- PTZ camera detected (Pan & Tilt controls visible)
- Tapo Care cloud storage promotion shown at bottom
