# Startup Flows - Tapo App

## Overview
This document captures UI flows encountered when starting the Tapo app on emulators. These flows may appear on fresh launches or after app updates.

## Coordinate System Discovery (2026-01-11)

**Critical Finding:** The emulator reports different physical vs logical coordinates.

| Metric | Value |
|--------|-------|
| Physical screen (`wm size`) | 720x1280 |
| Logical coordinates (uiautomator) | 320x640 |
| Density (`wm density`) | 160 dpi |
| **adb input tap uses** | **Logical (dp) coordinates** |

**Scaling NOT required** - `adb shell input tap` accepts dp coordinates directly.

Example:
```bash
# uiautomator shows: bounds="[83,565][236,640]"
# Center = (160, 603)
# Use directly:
adb shell input tap 160 603  # CORRECT
# NOT: adb shell input tap 360 1206  # WRONG (would be 2.25x scaled)
```

---

## Flow 1: Third-Party Services Popup

**When:** First launch after install, or periodically

**Screenshot:** `screenshots/startup-third-party-services.png`

### Screen 1: Service Selection
- Shows: Amazon Alexa, Google Assistant, Samsung SmartThings, IFTTT
- "Maybe Later" button at bottom

**Coordinates (320x640 dp):**
- Maybe Later: tap (160, 603)
- Back arrow: tap (24, 106)
- Amazon Alexa: tap (160, 268)
- Google Assistant: tap (160, 325)
- Samsung SmartThings: tap (160, 382)
- IFTTT: tap (160, 439)

**Dismissal:**
```bash
adb shell input tap 160 603  # Maybe Later
```

### Screen 2: Confirmation Tutorial
- Shows: Tutorial about finding Third-Party Services in Me tab
- "Got It" button at bottom

**Coordinates:**
- Got It: tap (160, 565)

**Full dismissal sequence:**
```bash
adb shell input tap 160 603  # Maybe Later
sleep 1
adb shell input tap 160 565  # Got It
```

---

## Flow 2: Device Unreachable

**When:** Camera is offline or network unreachable

**Screenshot:** `screenshots/startup-device-unreachable.png`

### Dialog Options
- "Details" - Shows troubleshooting tips
- "Remove" - Removes device from account
- "Cancel" - Dismisses dialog

**Coordinates (320x640 dp):**
- Details: tap (160, 504)
- Remove: tap (160, 556)
- Cancel: tap (160, 610)

**Resolution:**
1. Check camera power
2. Check camera WiFi connection
3. Check emulator network (must be on same network as camera)
4. Verify camera IP: 192.168.29.137

---

## Known Limitation: Video Blacks Out on Emulators

**Issue:** Live video feed shows briefly then blacks out on Android emulators.

**Key Discovery (2026-01-11):**
- Video **DOES render for a split second** when opening camera view
- Then immediately goes black
- PAN/Tilt controls **work correctly** (verified via physical phone on same account)
- Camera physically moves in response to emulator commands

**Symptoms:**
- Camera connects successfully (no "Device Unreachable" error)
- Privacy Mode can be toggled (blue icon shows streaming active)
- PTZ controls are accessible and responsive
- Video briefly visible, then blacks out

**Root Cause (Suspected):**
- **Anti-emulator protection** - Tapo app may detect emulator and disable video
- **GPU rendering handoff** - Software render works briefly, hardware acceleration fails
- **DRM/content protection** - Video stream protected against screen capture

**Workarounds:**
1. **Physical Android device** - Connect real phone via USB, run same automation
2. **scrcpy** - Mirror physical device to desktop for visual verification
3. **Take photo** - Use photo capture button to verify camera sees correctly
4. **Trust PAN commands** - Camera physically moves even without video feedback

**Impact on Automation:**
- UI automation still works (taps, navigation, controls)
- Cannot visually verify video content changes
- Image recognition for visual shift detection requires physical device

---

## Emulator Network Requirements

For camera connectivity, the emulator must:
1. Use **bridged networking** (not NAT) to reach local devices
2. Or camera must be accessible via internet (cloud mode)

Default emulator NAT cannot reach local network devices like 192.168.29.x.

**Workaround options:**
1. Use cloud-based camera access (TP-Link cloud)
2. Configure emulator with bridged networking
3. Use physical Android device on same WiFi

---

## Camera Card Icon States (Home Screen)

The camera card icon color indicates connection/streaming state:

| State | Icon Appearance | Meaning |
|-------|----------------|---------|
| Offline | Gray/muted, "Offline" label | Camera unreachable |
| Online + Privacy Mode ON | Normal icon | Connected but not streaming |
| Online + Privacy Mode OFF | **Blue icon** | Actively streaming |

**Screenshots:**
- `camera-offline-home-screen.png` - Gray icon, "Offline" label
- `camera-live-privacy-mode-active.png` - Connected but privacy on

This icon state can be used for automated state detection without opening the camera view.

---

## Session Checklist

Before starting camera automation:
- [ ] Emulator booted and ADB connected
- [ ] Tapo app launched
- [ ] Third-Party Services popup dismissed
- [ ] Camera shows "Online" status (not "Offline")
- [ ] Can tap camera card and see live feed

If camera offline, see "Device Unreachable" flow above.
