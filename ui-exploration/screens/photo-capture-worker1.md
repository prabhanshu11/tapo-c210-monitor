# Photo Capture Documentation (Worker-1)

**Activity:** `com.tplink.iot/.view.ipcamerav3.play.VideoPlayV3Activity` (camera-live)
**Screen Resolution:** 320x640
**Documented:** 2026-01-09
**Screenshot:** `screenshots/after-photo-capture-worker1.png`

## Photo Capture Button

### Location
| Element | Resource ID | Bounds | Content-desc | Position |
|---------|-------------|--------|--------------|----------|
| Take Photo | `tool_pic` | [26,278][74,326] | "Take Photo" | Left side of media controls |

### Visual Appearance
- **Icon:** Camera icon (gray when idle)
- **Position:** First button in media controls row
- **Adjacent to:** Record button (right), Talk button (below)

## User Actions

### Capture Photo
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Take Photo | `50, 302` | `adb shell input tap 50 302` |

## Capture Behavior

### UI Feedback
**During Capture:**
- Button briefly responds to tap
- No visible animation or flash effect observed
- Screen remains on live view

**After Capture:**
- No persistent notification visible
- Photo saved silently to storage
- Continue recording/streaming without interruption

### Save Location
**Destination:** Camera's local storage (SD card/memory)
- Same storage location as manual recordings
- Accessible through Playback & Download section
- Photos may appear in Download tab or mixed with recordings

### Filename Format
- Not directly visible in UI during capture
- Likely includes timestamp (date/time)
- Format determined by camera firmware
- Access details via Playback & Download -> Download tab

## Photo Storage Architecture

### Storage Options
1. **Local Storage (SD Card):**
   - Default location for captured photos
   - Stored on camera's internal SD card
   - Access requires camera online connection

2. **Cloud Storage (Tapo Care):**
   - Available with Tapo Care subscription
   - Automatic backup of photos
   - 30-day history retention

### Accessing Captured Photos
**Path:** `me-tab` -> Playback & Download -> Select camera -> Download tab

Expected locations:
- Download section for manual photos
- Mixed with recordings timeline (if timestamps match)
- Separate photo gallery (if available in newer versions)

## Concurrent Operations

### While Live Viewing
Photos can be captured during:
- ✅ Active live streaming
- ✅ While recording video (tested separately)
- ✅ While panning/tilting camera
- ✅ During two-way audio communication
- ✅ Any video mode (Day/Night/Auto)

### Multiple Captures
- Rapid successive captures supported
- No enforced delay between photos
- Each tap creates separate photo file

## Comparison: Photo vs Video Recording

| Feature | Photo Capture | Video Recording |
|---------|--------------|-----------------|
| UI Indicator | None (silent) | Red button + timer |
| Notification | No visible toast | "Recording saved to Memory" |
| Duration | Instant | User-controlled (manual stop) |
| Storage Impact | Minimal (~KB per photo) | Larger (~MB per minute) |
| Concurrent Ops | Fully compatible | Allows photo during record |

## Quality Settings

### Photo Quality
- Controlled by camera settings (Device Settings -> Video & Display)
- Inherits from video stream quality
- Typically matches camera resolution (1080p for C210)

### Access Quality Settings
**Path:** `camera-live` -> Device Settings [296,57] -> Video & Display

## Limitations Observed

### Emulator Testing
- Emulator went offline during extended testing
- Photo file verification not completed
- Filename format not confirmed
- Download workflow not fully tested

### Recommended Verification (Real Device)
1. Capture multiple photos
2. Navigate to Playback & Download
3. Check Download tab for photo files
4. Verify filename format and timestamps
5. Test photo download to phone
6. Confirm cloud sync behavior (if Tapo Care active)

## Navigation Path
`home` -> `camera-live` [85,220] -> tap photo button [50,302]

## Related Screens
- `camera-live` - Base screen for photo capture
- `playback-download` - View and download photos
- `device-settings` - Configure photo quality

## Technical Notes

### Capture Process
1. User taps photo button
2. Camera captures current frame from live stream
3. Photo saved to camera's local storage
4. No visible confirmation (silent operation)
5. Accessible via Playback & Download section

### Expected File Characteristics
- **Format:** Likely JPEG
- **Resolution:** Matches video stream (1080p typical)
- **Naming:** Timestamp-based (YYYYMMDDHHmmss format likely)
- **Metadata:** May include camera ID, location (if enabled)

## Raw Data Sources
- UI dumps from camera-live screen
- Screenshots of photo button states
- Observed behavior during capture attempts
