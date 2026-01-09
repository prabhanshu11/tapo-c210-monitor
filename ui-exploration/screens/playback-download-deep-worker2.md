# Playback & Download Screen - Deep Exploration (Worker 2)

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T07:10:00Z
**Package:** com.tplink.iot
**Path:** home -> me-tab -> Playback & Download -> Select Camera

## Screen Overview
The main playback library for viewing and downloading recorded videos from camera storage (SD card or cloud).

## Navigation Flow
```
Home -> Me Tab -> Playback & Download -> Camera Selection -> Playback Screen
```

---

## Camera Selection Screen (Intermediate)

### Structure
| Element | Resource ID | Type | Bounds | Clickable |
|---------|-------------|------|--------|-----------|
| Back | (ImageButton) | Button | [0,28][56,84] | Yes |
| Title | `toolbar_title` | TextView | "Camera" | No |
| Camera List | `rv_device_list` | RecyclerView | [0,88][320,168] | - |
| Camera Item | `device_list_item` | ViewGroup | [16,88][304,168] | Yes |
| Camera Icon | `img_icon` | ImageView | [32,104][80,152] | No |
| Camera Name | `tv_name` | TextView | "Tapo_C210_69A3" | No |
| Camera MAC | `tv_location` | TextView | "3C-64-CF-3C-69-A3" | No |

### Tap Coordinates
| Action | Tap Point | Description |
|--------|-----------|-------------|
| Select Camera | tap(160, 128) | Enter playback for this camera |
| Go Back | tap(28, 56) | Return to Me tab |

---

## Main Playback Screen

### Header Tabs (bounds: [47,24][273,88])

| Tab | Resource ID | Text | Bounds | Selected |
|-----|-------------|------|--------|----------|
| Playback | `tab_text` | "Playback" | [80,24][160,88] | Yes |
| Download | `tab_text` | "Download" | [160,24][240,88] | No |

### Video Player Area (bounds: [0,88][320,288])

| Element | Resource ID | Type | Content-Desc | Bounds |
|---------|-------------|------|--------------|--------|
| Video Container | `video_area` | RelativeLayout | "Video player, No Recordings" | [0,88][320,288] |
| Video Surface | `live_surface_view` | FrameLayout | - | [0,88][320,288] |
| Empty State | `live_default_background` | RelativeLayout | - | [0,88][320,288] |
| No Record Icon | `no_record_icon` | ImageView | - | [136,147][184,195] |
| Empty Text | `text_empty_or_error` | TextView | "No Recordings" | [104,205][216,228] |

### Video Toolbar (bounds: [0,240][320,288])

| Button | Resource ID | Content-Desc | Bounds | Enabled |
|--------|-------------|--------------|--------|---------|
| Play/Pause | `tool_play` | "Play" | [32,240][80,288] | No* |
| Mute/Unmute | `tool_sound` | "Mute" | [80,240][128,288] | No* |
| Screenshot | `tool_pic` | "Screenshot" | [128,240][176,288] | No* |
| Record Video | `tool_video` | "Record Video" | [176,240][224,288] | No* |
| Clip & Download | `tool_clip` | "Clip & Download" | [224,240][272,288] | No* |
| Fullscreen | `tool_full_screen` | "Fullscreen" | [272,240][320,288] | Yes |

*Disabled when no recording selected

### Date Navigation Bar (bounds: [0,298][320,346])

| Element | Resource ID | Type | Content-Desc | Bounds | Clickable |
|---------|-------------|------|--------------|--------|-----------|
| Previous Day | `rl_move_backward` | Button | "Last day" | [0,298][48,346] | Yes |
| Arrow Icon | `date_move_backward` | ImageView | - | [20,316][28,328] | No |
| Current Date | `date_cur_date` | TextView | "2026-01-09" | [48,298][148,346] | Yes |
| Next Day | `rl_move_forward` | Button | "Next day" | [148,298][196,346] | Yes |
| Arrow Icon | `date_move_forward` | ImageView | - | [168,316][176,328] | No |

### Storage Source Toggle (bounds: [177,298][296,346])

| Tab | Resource ID | Content-Desc | Bounds | Selected |
|-----|-------------|--------------|--------|----------|
| Cloud Video | `rl_cloud` | "Cloud Video, Tab 1 of 2" | [179,298][237,346] | No |
| SD Card | `rl_sd` | "microSD Card, Tab 2 of 2" | [238,298][296,346] | Yes |

### Recording List Area (bounds: [0,346][320,640])
When empty:
| Element | Resource ID | Type | Bounds |
|---------|-------------|------|--------|
| Empty Container | `layout_record_video_list_empty` | ViewGroup | [0,346][320,640] |
| Empty Image | `iv_no_recording` | ImageView | [60,413][260,535] |
| Empty Text | `tv_no_recording` | TextView | "No Recordings" | [108,551][213,573] |

---

## Quick Reference - Tap Coordinates

### Main Actions
| Action | Tap Point | Description |
|--------|-----------|-------------|
| Switch to Download tab | tap(200, 56) | View downloaded files |
| Go Back | tap(28, 56) | Return to camera selection |
| Previous Day | tap(24, 322) | View previous day's recordings |
| Next Day | tap(172, 322) | View next day's recordings |
| Select Date | tap(98, 322) | Open date picker |
| Cloud Videos | tap(208, 322) | Switch to cloud storage |
| SD Card Videos | tap(267, 322) | Switch to SD card storage |
| Play | tap(56, 264) | Play selected recording |
| Mute | tap(104, 264) | Toggle audio |
| Screenshot | tap(152, 264) | Capture screenshot from playback |
| Record | tap(200, 264) | Record from playback |
| Clip & Download | tap(248, 264) | Download clip |
| Fullscreen | tap(296, 264) | Enter fullscreen mode |

---

## ADB Command Sequences

### Navigate to Playback
```bash
# From home
adb -s emulator-5556 shell input tap 288 615  # Me tab
sleep 2
adb -s emulator-5556 shell input tap 160 354  # Playback & Download
sleep 2
adb -s emulator-5556 shell input tap 160 128  # Select camera
sleep 3
```

### Navigate Between Days
```bash
# Previous day
adb -s emulator-5556 shell input tap 24 322
sleep 2

# Next day
adb -s emulator-5556 shell input tap 172 322
sleep 2
```

### Switch Storage Source
```bash
# Cloud Video
adb -s emulator-5556 shell input tap 208 322
sleep 2

# SD Card
adb -s emulator-5556 shell input tap 267 322
sleep 2
```

### Switch to Download Tab
```bash
adb -s emulator-5556 shell input tap 200 56
sleep 2
```

---

## Recording Playback Workflow (When Recordings Exist)

### Expected UI When Recording Selected:
1. Video player shows recording preview/stream
2. Timeline scrubber appears below video
3. Toolbar buttons become enabled
4. Recording list shows clips with timestamps

### Available Actions During Playback:
- **Play/Pause** - Control video playback
- **Mute/Unmute** - Toggle audio
- **Screenshot** - Capture frame from recording
- **Record** - Save clip to local storage
- **Clip & Download** - Select time range and download
- **Fullscreen** - Landscape playback mode

---

## Key Resource IDs

| Purpose | Resource ID |
|---------|-------------|
| Main container | `playback_memory_content` |
| Header | `playback_memory_header` |
| Back button | `playback_memory_back` |
| Tab layout | `playback_memory_tab` |
| Video area | `video_area` |
| Video surface | `live_surface_view` |
| Control panel | `control_fragment` |
| Date controls | `play_back_top_bar` |
| Cloud toggle | `rl_cloud` |
| SD toggle | `rl_sd` |
| Empty list | `layout_record_video_list_empty` |
| Snackbar | `snackbar_text` |

---

## Storage Sources

### SD Card (microSD)
- Physical storage in camera
- Continuous recording or motion-triggered
- Access requires camera online
- Download transfers file to phone

### Cloud Video (Tapo Care)
- Requires Tapo Care subscription
- Motion-triggered clips
- 7-30 days retention (plan dependent)
- Stream directly, no download needed

---

## Notes
- Currently showing "No Recordings" - SD card may be empty or not inserted
- Date picker allows jumping to any date
- Cloud/SD toggle shows available storage sources
- Snackbar appears briefly with "No Recording" message
- Tooltip on first load explains cloud/SD toggle
