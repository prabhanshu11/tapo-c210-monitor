# Pan/Tilt Controls Documentation (Worker-1)

**Activity:** `com.tplink.iot/.view.ipcamerav3.play.VideoPlayV3Activity` (overlay on camera-live)
**Screen Resolution:** 320x640
**Documented:** 2026-01-09
**Screenshot:** `screenshots/pan-tilt-controls-worker1.png`

## Screen Structure

### Header Controls
| Element | Resource ID | Bounds | Content-desc | Clickable |
|---------|-------------|--------|--------------|-----------|
| Close Button (X) | `left_btn` | [0,357][48,405] | "close" | Yes |
| Settings Button | `right_btn` | [272,357][320,405] | "Pan/Tilt Control Settings" | Yes |

### Tab Navigation
**Container:** `title_container` - bounds [66,350][254,399]

| Tab | Bounds | Content-desc | Selected |
|-----|--------|--------------|----------|
| Pan/Tilt | [66,350][136,399] | "Pan/Tilt, Tab 1 of 3" | **Yes** |
| Patrol | [136,350][194,399] | "Patrol, Tab 2 of 3" | No |
| Pano (Beta) | [194,350][254,399] | "Pano, Beta feature, Tab 3 of 3" | No |

### Pan/Tilt Tab Content

#### Help Card
**Container:** `cv_viewpoint_debut_tips` - bounds [16,400][304,509]

| Element | Resource ID | Bounds | Text |
|---------|-------------|--------|------|
| Help Text | `tv_add_one_device` | [30,410][290,461] | "Mark your current position and you can quickly rotate your camera to the marked direction. Tap + to add one." |
| Close Link | `tv_viewpoint_debut_tips_close` | [228,461][276,509] | "close" |

#### Directional Control Pad
**Container:** `cloud_terrace_control_area` - bounds [0,509][320,640]
**Panel:** `panel` - bounds [81,514][239,640]

| Direction | Bounds | Content-desc | Tap Coordinates |
|-----------|--------|--------------|-----------------|
| Up | [142,514][177,568] | "Pan/Tilt Control Up" | `160, 541` |
| Down | [142,610][177,640] | "Pan/Tilt Control Down" | `160, 625` |
| Left | [81,575][135,610] | "Pan/Tilt Control Left" | `108, 592` |
| Right | [177,575][239,610] | "Pan/Tilt Control Right" | `208, 592` |

## User Actions

### Navigation
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Close PTZ Controls | `24, 381` | `adb shell input tap 24 381` |
| Open PTZ Settings | `296, 381` | `adb shell input tap 296 381` |
| Switch to Patrol Tab | `165, 374` | `adb shell input tap 165 374` |
| Switch to Pano Tab | `224, 374` | `adb shell input tap 224 374` |

### Camera Movement
| Action | Tap Coordinates | ADB Command |
|--------|-----------------|-------------|
| Move Up | `160, 541` | `adb shell input tap 160 541` |
| Move Down | `160, 625` | `adb shell input tap 160 625` |
| Move Left | `108, 592` | `adb shell input tap 108 592` |
| Move Right | `208, 592` | `adb shell input tap 208 592` |

## Behavior Notes

### Camera Movement
- **Control Type:** Directional buttons (not a continuous joystick)
- **Response:** Tap and hold to move, release to stop
- **Speed:** Controlled via PTZ Settings (accessed from settings button)

### Position Marking
- Users can mark current camera positions as viewpoints
- Tap "+" to add a new viewpoint at current position
- Marked positions allow quick rotation to saved directions

### Tab Functions
1. **Pan/Tilt:** Manual directional control (up/down/left/right)
2. **Patrol:** Automated patrol paths between marked positions
3. **Pano (Beta):** Panoramic/360° view functionality

## Discovered Screens
- `ptz-settings` - tap Settings button [296,381]
- `patrol-tab` - tap Patrol tab
- `pano-tab` - tap Pano tab

## Navigation Path
`home` -> `camera-live` -> tap Pan & Tilt [160,392] -> `pan-tilt-controls`

## Raw XML Reference
Dumped via: `adb -s emulator-5554 shell uiautomator dump /sdcard/ui.xml`
