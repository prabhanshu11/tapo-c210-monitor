# Camera Memory Screen - Deep Exploration (Worker 2)

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T07:15:00Z
**Package:** com.tplink.iot
**Path:** home -> me-tab -> Camera Memory

## Screen Overview
Local storage for photos and videos captured manually by the user from camera live view or playback. This is phone storage, NOT SD card or cloud storage.

## UI Structure

### Header (bounds: [0,24][320,88])

| Element | Resource ID | Type | Content-Desc | Bounds | Enabled |
|---------|-------------|------|--------------|--------|---------|
| Back | `memory_back` | Button | "Back" | [0,32][48,80] | Yes |
| Title | `toolbar_title` | TextView | "Camera Memory" | [106,32][214,80] | - |
| Filter | `memory_filter_action` | Button | "Filter" | [224,32][272,80] | Yes |
| Select | `memory_edit_action` | Button | "Select" | [272,32][320,80] | No* |

*Disabled when no media present

### Content Area (bounds: [0,88][320,640])

**Empty State:**
| Element | Resource ID | Type | Text | Bounds |
|---------|-------------|------|------|--------|
| Container | `fragment_memory_no_record_layout` | RelativeLayout | - | [0,24][320,640] |
| Empty Image | `no_record_found_iv` | ImageView | - | [0,176][320,332] |
| Empty Text | `tv_no_record_found` | TextView | "Photos and videos you take yourself will appear here." | [0,332][320,407] |

---

## Quick Reference - Tap Coordinates

### Header Actions
| Action | Tap Point | Description |
|--------|-----------|-------------|
| Go Back | tap(24, 56) | Return to Me tab |
| Filter | tap(248, 56) | Open filter options |
| Select Mode | tap(296, 56) | Enable multi-select (when media exists) |

---

## ADB Command Sequences

### Navigate to Camera Memory
```bash
# From home
adb -s emulator-5556 shell input tap 288 615  # Me tab
sleep 2
adb -s emulator-5556 shell input tap 160 410  # Camera Memory
sleep 2
```

### Open Filter Options
```bash
adb -s emulator-5556 shell input tap 248 56
sleep 1
```

### Go Back
```bash
adb -s emulator-5556 shell input tap 24 56
sleep 1
```

---

## Key Resource IDs

| Purpose | Resource ID |
|---------|-------------|
| Container | `fragment_photo_container` |
| Header | `layout_memory_header` |
| Back button | `memory_back` |
| Title | `toolbar_title` |
| Filter button | `memory_filter_action` |
| Select button | `memory_edit_action` |
| Empty layout | `fragment_memory_no_record_layout` |
| Empty image | `no_record_found_iv` |
| Empty text | `tv_no_record_found` |

---

## Expected Behavior (When Media Exists)

### Media Grid View
- Thumbnails of photos/videos in grid layout
- Grouped by date
- Tap to view full-screen
- Long-press for options

### Filter Options (Filter Button) - DOCUMENTED

**Type Filters:**
| Filter | Resource ID | Checkbox ID | Bounds |
|--------|-------------|-------------|--------|
| Photo | `image_item` | `image_check` | [16,127][304,186] |
| Video | `video_item` | `video_check` | [16,187][304,246] |
| Cloud Video | `cloud_video_item` | `cb_cloud_video_check` | [16,247][304,306] |
| Video Summary | `summary_video_item` | `cb_summary_video_check` | [16,307][304,366] |
| Moments | `splendid_moment_video_item` | `cb_splendid_moment_video_check` | [16,367][304,426] |
| Growth Record | `growth_record_video_item` | `cb_growth_record_video_check` | [16,427][304,486] |
| Facial Tracking | `face_tracking_item` | `cb_face_tracking_check` | [16,487][304,546] |

**Preference Filters:**
| Filter | Resource ID | Checkbox ID | Bounds |
|--------|-------------|-------------|--------|
| Favorite | `favorite_item` | `favorite_check` | [16,585][304,640] |

**Filter Actions:**
| Action | Resource ID | Bounds |
|--------|-------------|--------|
| Clear All | `memories_reset_filter` | [272,32][320,80] |
| Apply | `btn_bottom` | [20,569][300,618] |

**Filter Tap Coordinates:**
| Action | Tap Point |
|--------|-----------|
| Toggle Photo | tap(160, 156) |
| Toggle Video | tap(160, 216) |
| Toggle Cloud Video | tap(160, 276) |
| Toggle Video Summary | tap(160, 336) |
| Toggle Moments | tap(160, 396) |
| Toggle Growth Record | tap(160, 456) |
| Toggle Facial Tracking | tap(160, 516) |
| Toggle Favorite | tap(160, 612) |
| Clear All | tap(296, 56) |
| Apply | tap(160, 593) |

### Select Mode (Select Button)
When enabled:
- Checkboxes appear on thumbnails
- Multi-select for batch operations
- Delete, Share options appear

---

## Storage Details

### What Gets Saved Here:
1. **Screenshots from live view** (tool_pic button)
2. **Recorded clips from live view** (tool_video button)
3. **Downloaded clips from playback** (tool_clip button)
4. **Screenshots from playback**

### Storage Location:
- Phone's internal/external storage
- Typically: `/storage/emulated/0/Tapo/` or similar
- Not synced to cloud automatically

### File Naming Convention:
- Screenshots: `IMG_YYYYMMDD_HHMMSS.jpg`
- Videos: `VID_YYYYMMDD_HHMMSS.mp4`

---

## Relationship to Other Screens

### Playback & Download → Camera Memory
- Clips downloaded from Playback appear here
- Screenshots from playback saved here

### Camera Live → Camera Memory
- Screenshot button saves here
- Manual recording saves here

### Export Workflow
1. Capture/Download in camera-live or playback
2. Find in Camera Memory
3. Share/Export to other apps

---

## Notes
- This is LOCAL phone storage, not camera SD card
- Filter button allows sorting media
- Select button enables batch operations
- Empty when no manual captures made
- Different from SD Card recordings (accessed via Playback tab)
