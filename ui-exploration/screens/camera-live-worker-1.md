# Camera Live View Documentation (Worker-1)

**Activity:** `com.tplink.iot/.view.ipcamerav3.play.VideoPlayV3Activity`
**Screen Resolution:** 320x640
**Documented:** 2026-01-09

## Screen Structure

### Top Bar (Toolbar)
| Element | Resource ID | Bounds | Content-desc | Clickable | Notes |
|---------|-------------|--------|--------------|-----------|-------|
| Back Button | `btn_back` | [0,33][48,81] | "Back" | Yes | Returns to home screen |
| Camera Title | `title` | [92,45][229,68] | - | No | Text: "Tapo_C210_69A3" |
| Device Settings | `action_settings` | [272,33][320,81] | "Device Settings" | Yes | Opens device settings |

### Video Player Area
**Container:** `video_fragment` - bounds [0,88][320,336]

| Element | Resource ID | Bounds | Notes |
|---------|-------------|--------|-------|
| Live Surface Container | `live_surface_list_view_container` | [0,88][320,268] | Contains video stream |
| Live Surface View | `live_surface_view` | [0,88][320,268] | Actual video player |
| Accessibility Mask | `accessibility_mask_view` | [0,88][320,268] | SeekBar, content-desc: "Camera Live Player, Streaming" |
| Touch Mask | `view_touch_mask` | [0,88][320,268] | Touch overlay for gestures |

### Video Overlay Controls (bottom of video)
**Container:** `pop_bar_in_bottom` - bounds [0,220][320,268]

| Element | Resource ID | Bounds | Content-desc | Text | Clickable |
|---------|-------------|--------|--------------|------|-----------|
| Multi-View | `tool_view` | [44,220][92,268] | "Switch to Multi-View" | - | Yes |
| Video Mode | `tv_infrared_mode` | [136,220][184,268] | "Video Mode, Auto" | "Auto" | Yes |
| Fullscreen | `tool_full_screen` | [228,220][276,268] | "Fullscreen" | - | Yes |

### Media Controls Bar
**Container:** `toolbar_in_bottom` - bounds [0,268][320,336]

| Element | Resource ID | Bounds | Content-desc | Clickable |
|---------|-------------|--------|--------------|-----------|
| Take Photo | `tool_pic` | [26,278][74,326] | "Take Photo" | Yes |
| Manual Recording | `record_container` | [99,278][147,326] | "Manual Recording" | Yes |
| Record Video Icon | `tool_video` | [99,278][147,326] | "Record Video" | Yes |
| Mic Volume | `tool_sound` | [173,278][221,326] | "Camera's Microphone Volume" | Yes |
| Voice Call | `tool_voice_call` | [246,278][294,326] | "Voice Call" | Yes |

### Control Panel (Main Actions)
**Container:** `sv_control_layout` (ScrollView) - bounds [0,336][320,640]

#### Row 1: `first_unit_ll` [16,350][304,433]
| Element | Resource ID | Bounds | Content-desc | Text Label |
|---------|-------------|--------|--------------|------------|
| Talk | `talk_tv` | [16,350][112,433] | "Talk" | "Talk" |
| Pan & Tilt | `control_tv` | [112,350][208,433] | "Pan and Tilt Controls" | "Pan & Tilt" |
| Detection Alarm | `call_tv` | [208,350][304,433] | "Detection Alarm, Off" | "Alarm Off" |

#### Row 2: `second_unit_ll` [16,433][304,529]
| Element | Resource ID | Bounds | Content-desc | Text Label |
|---------|-------------|--------|--------------|------------|
| Privacy Mode | `privacy_tv` | [16,433][112,516] | "Privacy Mode, Off" | "Privacy Mode" |
| Tapo Care | `alerts_tv` | [112,433][208,516] | "Tapo Care" | "Tapo Care" |

### Cloud Storage Section
**Container:** `fl_cloud_storage_fragment` - bounds [16,529][304,640]

| Element | Resource ID | Bounds | Content-desc | Notes |
|---------|-------------|--------|--------------|-------|
| Playback & Download | `playback_and_download` | [16,545][304,608] | "Playback & Download" | Button with icon |
| Cloud Storage Banner | `layout_play_storage_server` | [16,624][304,640] | "Tapo Care Cloud Storage, Enjoy up to 30 days..." | Marketing banner |
| Dismiss Banner | `iv_cloud_service_close` | [256,624][304,640] | "Dismiss" | Close button on banner |

## Interactive Elements Summary

### Primary Actions
1. **Take Photo** [26,278][74,326] - Captures still image
2. **Record Video** [99,278][147,326] - Starts/stops manual recording
3. **Talk** [16,350][112,433] - Two-way audio communication
4. **Pan & Tilt** [112,350][208,433] - Opens PTZ controls (discovered screen: `pan-tilt-controls`)
5. **Privacy Mode Toggle** [16,433][112,516] - Enables/disables privacy mode

### Camera Controls
1. **Mic Volume** [173,278][221,326] - Adjust camera microphone (discovered screen: `volume-control`)
2. **Voice Call** [246,278][294,326] - Initiates voice call
3. **Detection Alarm** [208,350][304,433] - Toggle motion detection alarm

### Video Display Controls
1. **Multi-View** [44,220][92,268] - Switch to multi-camera view (discovered screen: `multi-view`)
2. **Video Mode** [136,220][184,268] - Toggle day/night/auto mode (discovered screen: `video-mode-picker`)
3. **Fullscreen** [228,220][276,268] - Enter fullscreen mode (discovered screen: `fullscreen-live`)

### Navigation Actions
1. **Back** [0,33][48,81] - Return to home screen
2. **Device Settings** [272,33][320,81] - Opens camera settings (discovered screen: `device-settings`)
3. **Playback & Download** [16,545][304,608] - Opens video library (discovered screen: `playback`)
4. **Tapo Care** [112,433][208,516] - Opens Tapo Care subscription (discovered screen: `tapo-care`)

## Discovered Screens (for queue)
- `device-settings` - tap settings icon
- `pan-tilt-controls` - tap Pan & Tilt button
- `playback` - tap Playback & Download
- `fullscreen-live` - tap fullscreen button
- `multi-view` - tap multi-view button
- `video-mode-picker` - tap video mode (Auto/Day/Night)
- `tapo-care` - tap Tapo Care button
- `volume-control` - tap mic volume button

## Special States
- **Streaming Active:** SeekBar shows "Camera Live Player, Streaming"
- **Privacy Mode:** Currently "Off" - when enabled, video stream blocked
- **Detection Alarm:** Currently "Off"
- **Video Mode:** Currently "Auto"

## Navigation Path
`home` -> tap camera card -> `camera-live`

## Raw XML Reference
Dumped via: `adb -s emulator-5554 shell uiautomator dump /sdcard/ui.xml`
