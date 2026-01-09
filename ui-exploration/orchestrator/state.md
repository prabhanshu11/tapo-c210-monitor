# Orchestrator State

## Status: RUNNING

## Active Workers
- worker-1: ⏸️ IDLE - needs restart (emulator-5554 ✅)
- worker-2: ⏸️ IDLE - needs restart (emulator-5556 ✅)
- worker-3: ⏸️ WAITING - needs emulator-5558 started

## Commands
<!-- Write commands for workers here, they will poll this file -->
<!-- Format: worker-N: COMMAND [args] -->

### Active Commands (workers poll this on restart):

**worker-1: DEEP EXPLORE - Camera Controls & Recording**
Path: home -> camera-live [85,220] -> explore these:
1. Pan & Tilt [160,392] - joystick, presets, speed
2. Recording [123,302] - start/stop, UI changes, save location
3. Playback & Download [160,577] - recordings list, download, export
4. Photo capture [50,302] - where saved, filename format

**worker-2: DEEP EXPLORE - Camera Memory & Playback Details**
Path: home -> me-tab [288,615] -> explore these:
1. Playback & Download [160,354] - full library exploration
2. Camera Memory [160,410] - SD card status, storage management
3. Back to camera-live -> test recording -> verify in playback

**worker-3: DEEP EXPLORE - Device Settings (if emulator-5558 available)**
Path: home -> camera-live -> device-settings [296,57]
Document ALL settings categories, detection zones, notification config

### Exploration Priority (USER-REQUESTED):
**DEEP DIVE - Camera Recording & Transfer Workflow:**
1. **Pan/Tilt Controls** - Document joystick behavior, preset positions, speed
2. **Zoom Controls** - Digital zoom levels, pinch gestures, zoom buttons
3. **Recording Workflow:**
   - What happens when recording starts (UI changes, indicators)
   - Where recordings are saved (SD card? cloud? phone?)
   - Filename format and organization
   - Recording duration limits
4. **File Transfer:**
   - How to download recordings to phone
   - Playback & Download screen - full exploration
   - Export options, sharing capabilities
   - Wireless transfer methods (WiFi direct? cloud?)
5. **Camera Memory Management:**
   - SD card status and formatting
   - Storage allocation
   - Auto-overwrite settings

### Screenshot Protocol:
When documenting a screen, workers MUST:
1. Capture screenshot: `adb -s [emulator] exec-out screencap -p > screenshots/<screen-name>-worker-N.png`
2. Save to: `ui-exploration/screenshots/<screen-name>-worker-N.png`
3. Resize if needed: `convert <file>.png -resize 'x1900>' <file>.png`

## Stats
- Screens discovered: 32+ (expanding as workers explore)
- Screens documented: 5 (home, camera-live, cameras-tab, me-tab, smart-tab)
- Screens with consensus: 4 (home, camera-live, me-tab, smart-tab)
- Pending merges: 0
- Issues: 1 (device-settings ANR on emulator-5554)

## Log
- 2026-01-09 06:35 - System initialized
- 2026-01-09 06:35 - Orchestrator online, waiting for emulators
- 2026-01-09 06:35 - Pre-assigned: worker-1 -> home, worker-2 -> camera-live
- 2026-01-09 06:42 - emulator-5554 connected
- 2026-01-09 06:42 - Worker 3 agent active, waiting for emulator-5558
- 2026-01-09 06:43 - emulator-5556 connected
- 2026-01-09 06:43 - Worker 1 WORKING on "home" (claimed from queue)
- 2026-01-09 06:44 - Worker 2 also claiming "home" for consensus coverage
