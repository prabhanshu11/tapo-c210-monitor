# Tapo App UI Automation Plan

## Goal
Automate the Tapo app to:
1. View live camera feed
2. Control pan/tilt movement

## App UI Structure

### Screen 1: Home Page
- Shows device cards for each camera
- Bottom nav: **Home** | Cameras | Smart | Me
- **Action**: Tap camera card (e.g., "Tapo C210") to enter live view

### Screen 2: Live View Page
After tapping camera card, full-screen video feed appears.

**Top Bar:**
- Back arrow (←) - return to home
- Camera name
- Gear icon (⚙️) - settings

**Bottom Control Bar:**
| Icon | Function |
|------|----------|
| Screenshot | Save frame to Downloads |
| Record | Start/stop recording |
| Volume | Adjust audio |
| Talk | Two-way audio |
| **Pan & Tilt** | Opens pan/tilt control panel |
| Alarm | Motion alarm toggle |
| Privacy Mode | Disable surveillance |

**Other Controls:**
- Multi-Screen icon
- Video Quality (2K QHD / 720P)
- Video Mode (Day/Night/Auto)
- Full Screen button

### Screen 3: Pan & Tilt Control Panel
Accessed by tapping "Pan & Tilt" button on live view.

**Layout:**
```
        [↑]
    [←] [●] [→]
        [↓]
```

**Controls:**
- Directional arrows: Move camera (degrees configurable in settings)
- Patrol buttons:
  - Vertical Patrol - scan up/down once
  - Horizontal Patrol - scan left/right once
- Mark Position - save current angle for quick recall
- Settings gear - adjust degrees per tap

## Automation Steps

### Task 1: Get Live Feed
```
1. Launch app: com.tplink.iot
2. Wait for Home page (look for camera cards)
3. Tap first camera card
4. Wait for live view to load
5. Verify video stream visible
```

**UI Elements to detect:**
- Home: `text="Tapo C210"` or device name
- Live view: Video player element, control bar visible

### Task 2: Pan Camera
```
1. From live view, tap "Pan & Tilt" button
2. Wait for control panel to appear
3. Tap directional button (↑/↓/←/→)
4. Camera moves
5. Optionally tap back/close to return
```

**UI Elements to detect:**
- Pan & Tilt button: `text="Pan & Tilt"` or icon with content-desc
- Directional controls: Arrow buttons or swipe gestures

### Task 3: Set Position Preset
```
1. Navigate to desired angle using pan/tilt
2. Tap "Mark Position" or star icon
3. Save preset
4. Later: Tap saved position to return instantly
```

## ADB Commands Reference

### Launch app
```bash
adb shell am start -n com.tplink.iot/.activity.SplashActivity
```

### Get current screen
```bash
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml /tmp/ui.xml
```

### Tap coordinates
```bash
adb shell input tap X Y
```

### Swipe (for pan gesture if supported)
```bash
adb shell input swipe X1 Y1 X2 Y2 duration_ms
```

## Challenges to Handle

1. **First-time setup**: May need to log in / add camera first
2. **Camera offline**: Handle "camera not available" state
3. **Network latency**: Video may take time to load
4. **Permission dialogs**: Camera/mic permissions on first launch
5. **Element visibility**: Controls may hide after timeout - tap screen to show

## Sources
- [TP-Link Pan & Tilt FAQ](https://www.tp-link.com/us/support/faq/2623/)
- [Tapo Camera App Guide](https://www.tapo.com/us/faq/166/)
- [Tapo C210 Product Page](https://www.tapo.com/us/product/smart-camera/tapo-c210/)
