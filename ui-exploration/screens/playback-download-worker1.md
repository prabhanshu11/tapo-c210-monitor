# Playback & Download Documentation (Worker-1)

**Activities:**
- `com.tplink.iot/.view.me.PaneListCommonActivity` (Camera selection)
- `com.tplink.iot/.view.cloudvideo.TapoPlaybackAndDownloadActivity` (Recordings library)
**Screen Resolution:** 320x640
**Documented:** 2026-01-09
**Screenshots:**
- `screenshots/playback-download-library-worker1.png`
- `screenshots/playback-recordings-list-worker1.png`

## Access Paths

### Path 1: From Camera Live View
`home` -> `camera-live` -> Playback & Download button [160,577]
**Result:** App becomes unresponsive (ANR) - not recommended path

### Path 2: From Me Tab (Recommended)
`home` -> Me tab [288,615] -> Playback & Download [160,354] -> Select camera
**Result:** Successful navigation to recordings library

## Screen 1: Camera Selection
**Activity:** `com.tplink.iot/.view.me.PaneListCommonActivity`
**Screenshot:** `playback-download-library-worker1.png`

### Structure
| Element | Bounds | Content | Clickable |
|---------|--------|---------|-----------|
| Back Button | [0,33][48,81] | "<" | Yes |
| Title | Center | "Camera" | No |
| Camera Card | [32,88][288,152] | Camera icon + details | Yes |
| Camera Icon | [40,88][80,152] | Blue camera image | No |
| Camera Name | [97,96][271,119] | "Tapo_C210_69A3" | No |
| Camera MAC | [97,123][216,140] | "3C-64-CF-3C-69-A3" | No |
| Arrow | [256,108][288,140] | ">" | No |

### User Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Go Back | `24, 57` | `adb shell input tap 24 57` |
| Select Camera | `160, 120` | `adb shell input tap 160 120` |

## Screen 2: Recordings Library (Empty State)
**Activity:** `com.tplink.iot/.view.cloudvideo.TapoPlaybackAndDownloadActivity`
**Screenshot:** `playback-recordings-list-worker1.png`

### Header Section
| Element | Bounds | Content | State |
|---------|--------|---------|-------|
| Back Button | [0,33][48,81] | "<" | Enabled |
| Playback Tab | ~[83,33][147,54] | "Playback" (blue, selected) | Active |
| Download Tab | ~[147,33][226,54] | "Download" | Inactive |

### Main Content Area (Empty State)

#### No Recordings Message
| Element | Position | Content |
|---------|----------|---------|
| Icon | Center-top | Crossed-out video icon |
| Message | Center | "No Recordings" (gray text) |

#### Date Selector
| Element | Bounds | Content | Clickable |
|---------|--------|---------|-----------|
| Previous Day | [18,308][34,324] | "<" | Yes |
| Current Date | Center | "2026-01-09" | No |
| Next Day | [162,308][178,324] | ">" | Yes |

#### Storage Source Toggle (Tutorial Overlay)

**First-time User Tutorial:**
- **Visual:** Animated illustration showing Cloud ⇄ SD Card toggle
- **Message:** "Cloud Video ⇄ SD Card"
- **Icon:** Cloud icon with SD card icon
- **Pointer:** Yellow arrow pointing to toggle
- **Close Button:** "Close" button to dismiss tutorial [215,453][297,485]

**Toggle Location:** Top-right area
- **Cloud Icon:** Left side of toggle
- **SD Card Icon:** Right side of toggle (with yellow highlight)
- **Default:** SD Card (local storage) selected

### User Actions
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Go Back | `24, 57` | `adb shell input tap 24 57` |
| Switch to Download Tab | `186, 54` | `adb shell input tap 186 54` |
| Previous Day | `26, 316` | `adb shell input tap 26 316` |
| Next Day | `170, 316` | `adb shell input tap 170 316` |
| Close Tutorial | `256, 469` | `adb shell input tap 256 469` |
| Toggle Cloud/SD Card | ~`237, 329` | `adb shell input tap 237 329` |

## Recording Storage Architecture

### Storage Locations
1. **SD Card (Local):**
   - Recordings saved directly to camera's SD card
   - Default storage location for manual recordings
   - Access requires camera to be online

2. **Cloud (Tapo Care):**
   - Requires Tapo Care subscription
   - Unlimited cloud storage with 30-day history
   - Event-based recording with motion detection

### Viewing Recordings
1. Navigate to Playback & Download
2. Select camera from list
3. Choose storage source (Cloud or SD Card)
4. Select date using date picker
5. Recordings appear as timeline or list items
6. Tap recording to play

## Tab Functions

### Playback Tab
- Browse recordings by date
- Play recordings directly
- Timeline view of events
- Filter by storage source (Cloud/SD Card)

### Download Tab
- Download recordings to phone
- Export videos for sharing
- Manage downloaded content
- View download progress

## Navigation Paths

### To Playback & Download
**From Me Tab (Recommended):**
```
home [32,615] -> me-tab [288,615] -> Playback & Download [160,354] -> Select camera [160,120]
```

**From Camera Live (Not Recommended - causes ANR):**
```
home [32,615] -> camera-live [85,220] -> Playback & Download [160,577]
```

## Issues Encountered

### ANR on Direct Access
**Trigger:** Tapping "Playback & Download" from camera-live view
**Result:** "Tapo isn't responding" dialog
**Workaround:** Access via Me tab instead
**Status:** Consistent issue on emulator-5554

## Discovered Features

### Storage Management
- Toggle between Cloud and SD Card storage
- Date-based navigation for recordings
- Separate tabs for playback vs download

### Tutorial System
- First-time overlay explains Cloud/SD Card toggle
- Animated illustrations with pointers
- Dismissible with "Close" button

## Related Screens
- `camera-live` - Source of recordings
- `recording-workflow` - How recordings are created
- `me-tab` - Alternative access point
- `camera-memory-management` - SD card settings (Me tab -> Camera Memory)

## Raw XML Reference
Dumped via: `adb -s emulator-5554 shell uiautomator dump /sdcard/ui.xml`
