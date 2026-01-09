# Recording Workflow Documentation (Worker-1)

**Activity:** `com.tplink.iot/.view.ipcamerav3.play.VideoPlayV3Activity`
**Screen Resolution:** 320x640
**Documented:** 2026-01-09
**Screenshots:**
- `screenshots/camera-live-before-recording-worker1.png`
- `screenshots/recording-active-worker1.png`
- `screenshots/recording-active-11sec-worker1.png`
- `screenshots/recording-stopped-worker1.png`

## Recording States

### State 1: Idle (Ready to Record)
**Screenshot:** `camera-live-before-recording-worker1.png`

| Element | Resource ID | State | Visual |
|---------|-------------|-------|--------|
| Record Button | `tool_video` | Enabled | Gray record icon |
| Timer Display | - | Hidden | Not visible |

### State 2: Recording Active
**Screenshot:** `recording-active-worker1.png`

| Element | Resource ID | State | Visual | Bounds |
|---------|-------------|-------|--------|--------|
| Record Button | `tool_video` | Active | Red pulsing circle | [99,278][147,326] |
| Timer Display | - | Visible | "00:00:06" (red text) | Below record button |

**UI Changes When Recording:**
1. Record button changes from gray to **red pulsing circle**
2. **Timer appears** in red text showing elapsed time (format: HH:MM:SS)
3. Camera continues streaming live video
4. Other controls remain accessible (photo, mic, voice call)

### State 3: Recording Stopped
**Screenshot:** `recording-stopped-worker1.png`

**Notification:** Black toast at top of screen
- Text: **"Recording saved to Memory."**
- Position: Top of screen (overlays video area)
- Duration: ~2-3 seconds
- Style: Dark background, white text

## User Actions

### Start Recording
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Start Recording | `123, 302` | `adb shell input tap 123 302` |

### Stop Recording
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Stop Recording | `123, 302` | `adb shell input tap 123 302` |

**Note:** Same button toggles recording on/off

## Recording Behavior

### Save Location
- **Destination:** Camera's SD card (device memory)
- **Notification:** "Recording saved to Memory" confirms successful save
- **Access:** Via Playback & Download screen

### Recording Duration
- **Tested:** Successfully recorded 11+ seconds
- **Limit:** Not encountered during testing
- **Stop Method:** Manual (user must tap stop button)

### Filename Format
- Not directly visible in UI
- Accessible through Playback & Download section
- Organized by date (visible in playback screen: "2026-01-09")

## Integration with Playback

### Viewing Recordings
**Path:** `camera-live` -> Playback & Download [160,577] -> Select camera -> Select date

**Storage Toggle:**
- Cloud Video ⇄ SD Card toggle available in playback screen
- Default: SD Card (local storage on camera)

## Technical Notes

### Recording Process
1. User taps record button
2. UI immediately updates (red button, timer starts)
3. Video streams to camera's SD card
4. User taps stop when finished
5. System saves recording and shows confirmation toast
6. Recording appears in Playback & Download library

### Concurrent Operations
While recording:
- ✅ Can take photos
- ✅ Can adjust mic volume
- ✅ Can initiate voice call
- ✅ Can pan/tilt camera
- ✅ Can toggle video mode (Day/Night/Auto)
- ❓ Multi-view (not tested during recording)

## Navigation Path
`home` -> `camera-live` -> tap record button [123,302]

## Related Screens
- `camera-live` - Base screen for recording
- `playback-download-library` - View saved recordings
- `playback-recordings-list` - Browse recordings by date

## Raw Data Sources
- UI dumps from recording states
- Screenshots showing state transitions
- Toast notification for save confirmation
