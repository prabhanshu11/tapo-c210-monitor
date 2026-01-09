# Camera Live Screen (CONSENSUS)

**Activity:** `com.tplink.iot/.view.ipcamerav3.play.VideoPlayV3Activity`
**Screen Resolution:** 320x640
**Confirmed by:** Worker-1, Worker-2
**Consensus reached:** 2026-01-09

## Screen Structure

### Header/Toolbar [0,24][320,88]
| Element | Resource ID | Bounds | Content-desc | Clickable | Confirmed |
|---------|-------------|--------|--------------|-----------|-----------|
| Back Button | `btn_back` | [0,33][48,81] | "Back" | Yes | ✅ Both |
| Camera Title | `title` | [92,45][229,68] | - | No | ✅ Both |
| Device Settings | `action_settings` | [272,33][320,81] | "Device Settings" | Yes | ✅ Both |

### Video Player Area [0,88][320,268]
| Element | Resource ID | Bounds | Notes | Confirmed |
|---------|-------------|--------|-------|-----------|
| Video Container | `live_surface_list_view_container` | [0,88][320,268] | FrameLayout | ✅ Both |
| Video Surface | `live_surface_view` | [0,88][320,268] | Actual player | ✅ Both |
| Player Mask | `accessibility_mask_view` | [0,88][320,268] | "Camera Live Player, Streaming" | ✅ Both |
| Touch Mask | `view_touch_mask` | [0,88][320,268] | Touch overlay | ✅ Both |

### Video Bottom Bar [0,220][320,268]
| Element | Resource ID | Bounds | Content-desc | Text | Confirmed |
|---------|-------------|--------|--------------|------|-----------|
| Multi-View | `tool_view` | [44,220][92,268] | "Switch to Multi-View" | - | ✅ Both |
| Video Mode | `tv_infrared_mode` | [136,220][184,268] | "Video Mode, Auto" | "Auto" | ✅ Both |
| Fullscreen | `tool_full_screen` | [228,220][276,268] | "Fullscreen" | - | ✅ Both |

### Media Controls Bar [0,268][320,336]
| Element | Resource ID | Bounds | Content-desc | Confirmed |
|---------|-------------|--------|--------------|-----------|
| Take Photo | `tool_pic` | [26,278][74,326] | "Take Photo" | ✅ Both |
| Record Video | `record_container` | [99,278][147,326] | "Manual Recording" | ✅ Both |
| Record Icon | `tool_video` | [99,278][147,326] | "Record Video" | ✅ Both |
| Mic Volume | `tool_sound` | [173,278][221,326] | "Camera's Microphone Volume" | ✅ Both |
| Voice Call | `tool_voice_call` | [246,278][294,326] | "Voice Call" | ✅ Both |

### Control Panel - Row 1 [16,350][304,433]
| Element | Resource ID | Bounds | Content-desc | Label | Confirmed |
|---------|-------------|--------|--------------|-------|-----------|
| Talk | `talk_tv` | [16,350][112,433] | "Talk" | "Talk" | ✅ Both |
| Pan & Tilt | `control_tv` | [112,350][208,433] | "Pan and Tilt Controls" | "Pan & Tilt" | ✅ Both |
| Detection Alarm | `call_tv` | [208,350][304,433] | "Detection Alarm, Off" | "Alarm Off" | ✅ Both |

### Control Panel - Row 2 [16,433][304,516]
| Element | Resource ID | Bounds | Content-desc | Label | Confirmed |
|---------|-------------|--------|--------------|-------|-----------|
| Privacy Mode | `privacy_tv` | [16,433][112,516] | "Privacy Mode, Off" | "Privacy Mode" | ✅ Both |
| Tapo Care | `alerts_tv` | [112,433][208,516] | "Tapo Care" | "Tapo Care" | ✅ Both |

### Storage Section [16,529][304,640]
| Element | Resource ID | Bounds | Content-desc | Confirmed |
|---------|-------------|--------|--------------|-----------|
| Playback & Download | `playback_and_download` | [16,545][304,608] | "Playback & Download" | ✅ Both |
| Cloud Storage Banner | `layout_play_storage_server` | [16,624][304,640] | "Tapo Care Cloud Storage, Enjoy up to 30 days..." | ✅ Both |
| Dismiss Banner | `iv_cloud_service_close` | [256,624][304,640] | "Dismiss" | ✅ Both |

## Navigation Actions (VERIFIED)

### Primary Actions
| Action | Bounds | Target Screen | Confirmed |
|--------|--------|---------------|-----------|
| Tap Back | [0,33][48,81] | `home` | ✅ Both |
| Tap Settings | [272,33][320,81] | `device-settings` | ✅ Both |
| Tap Take Photo | [26,278][74,326] | Capture action | ✅ Both |
| Tap Record | [99,278][147,326] | Toggle recording | ✅ Both |
| Tap Talk | [16,350][112,433] | Push-to-talk | ✅ Both |

### PTZ & Video Controls
| Action | Bounds | Target Screen | Confirmed |
|--------|--------|---------------|-----------|
| Tap Pan & Tilt | [112,350][208,433] | `pan-tilt-controls` | ✅ Both |
| Tap Multi-View | [44,220][92,268] | `multi-view` | ✅ Both |
| Tap Video Mode | [136,220][184,268] | `video-mode-picker` | ✅ Both |
| Tap Fullscreen | [228,220][276,268] | `fullscreen-live` | ✅ Both |

### Settings & Subscriptions
| Action | Bounds | Target Screen | Confirmed |
|--------|--------|---------------|-----------|
| Tap Mic Volume | [173,278][221,326] | `volume-control` | ✅ W1 only |
| Tap Voice Call | [246,278][294,326] | `voice-call` | ✅ W2 only |
| Tap Tapo Care | [112,433][208,516] | `tapo-care` | ✅ Both |
| Tap Playback | [16,545][304,608] | `playback` | ✅ Both |

### Toggles (State Actions)
| Action | Bounds | Current State | Confirmed |
|--------|--------|---------------|-----------|
| Tap Detection Alarm | [208,350][304,433] | Off | ✅ Both |
| Tap Privacy Mode | [16,433][112,516] | Off | ✅ Both |

## Key Resource IDs
- `fl_root` - Root frame layout
- `coordinator_layout` - Main scrollable container
- `video_fragment` - Video player container
- `live_surface_list_view` - Video surface grid
- `pop_bar_in_bottom` - Video overlay controls
- `toolbar_in_bottom` - Media capture toolbar
- `ll_control_panel` - Control buttons panel
- `sv_control_layout` - Scrollable control area
- `fl_cloud_storage_fragment` - Storage/playback section

## States
- **Video Mode:** "Auto" (Day/Night/Auto options)
- **Detection Alarm:** Off (toggleable)
- **Privacy Mode:** Off (toggleable)
- **Streaming Status:** "Camera Live Player, Streaming"

## Navigation Path
`home` -> tap camera card [16,160][154,280] -> `camera-live`

## Notes
- PTZ camera (Pan & Tilt controls present)
- Two-way audio supported (Talk, Voice Call)
- Manual recording and photo capture available
- Tapo Care cloud storage promotion at bottom
- Video area: 88-336px height, controls scrollable below
