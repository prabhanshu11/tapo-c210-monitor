# Plan: Fix Live Video Feed

## The Broader Vision

You're building an **intelligent home automation system** with multiple components:

| Component | Purpose | Status |
|-----------|---------|--------|
| **omarchy-voice-typing** | Voice input via AssemblyAI | ✅ Working |
| **datalake** | Data storage (audio, transcripts, screenshots) | ✅ Working |
| **UI-agent** | Browser automation (PPE loop) | ✅ Working |
| **shopping-agent** | Multi-platform shopping | 🔄 In progress |
| **usb-webcam-api** | USB camera streaming | ✅ Working |
| **tapo-c210-monitor** | WiFi camera integration | ❌ **BLOCKED** |

**The Tapo camera is meant to provide visual awareness** - detecting presence, monitoring spaces, enabling visual-triggered automations. Without video feed, it's just a remote-controlled PTZ motor.

**Claude Agent SDK Integration Potential**:
1. Voice → Intent → Camera Action (e.g., "Look at the front door")
2. Camera Feed → LLM Vision → Event Detection → Automation
3. Visual state + Voice commands → Context-aware responses
4. Multi-camera monitoring → Unified situational awareness

---

## The Actual Problem
**Goal**: Get live video feed from Tapo C210 camera to computer for intelligent home automation.

**Current State**: Video blacks out immediately after a brief flash.

**Root Cause**: MQTT connection failure
```
MediaException{errorCode=-2016, message='Don't exist mqtt connection!'}
```
- Video streaming uses MQTT via TP-Link cloud relay
- MQTT connection fails/disconnects on emulator
- PAN/Tilt controls work ✅ CONFIRMED (they use HTTP/REST, different pathway)

## What I Was Doing Wrong
I got distracted by:
- CPU/memory optimization (PAG library issues)
- Parallel emulator strategies
- Performance tuning

These are **secondary issues**. The PRIMARY blocker is: **video doesn't work at all**.

---

## Investigation Plan

### Phase 1: Verify Direct Camera Access (30 min)
The README mentions RTSP URLs work, but progress_actual.md says ports are closed.

**Action**: Re-test camera ports after checking Tapo app settings
1. Check "Third-Party Compatibility" in Tapo app (Settings > Tapo Lab)
2. Check if RTSP can be enabled in camera settings
3. Re-scan ports: 554 (RTSP), 2020 (ONVIF), 443, 80
4. Test with VLC: `vlc rtsp://admin:<pass>@192.168.29.137:554/stream1`

**If RTSP works**: Problem solved - use direct stream, skip emulator entirely.

### Phase 2: Investigate MQTT Failure on Emulator (1 hour)
If direct access doesn't work, investigate why MQTT fails.

**Hypotheses**:
1. **Emulator network configuration** - NAT/bridge issues
2. **TP-Link anti-emulator detection** - Device fingerprinting
3. **SSL/TLS certificate issues** - Cloud relay rejects emulator
4. **Timing/latency** - Connection times out

**Investigation steps**:
1. Capture full logcat during video attempt
2. Search for MQTT connection attempts, errors
3. Check network configuration (`adb shell ip route`, `adb shell getprop`)
4. Compare with physical device logs (if available)
5. Try different emulator network modes (NAT vs bridged)

### Phase 3: Alternative Approaches (if Phases 1-2 fail)

**Option A: Static Thumbnails Workaround**
- "Cameras" tab shows static thumbnails without triggering live stream
- Thumbnails load successfully without ANR
- Could capture periodic snapshots for visual monitoring
- **Limitation**: Not real-time, low frame rate

**Option B: Web Interface**
- Check if Tapo has web interface (my.tp-link.com)
- May be able to view video in browser
- Could use browser automation instead of Android

**Option C: MITM Cloud Traffic**
- Intercept HTTPS traffic between app and TP-Link cloud
- Extract video stream protocol
- **Risk**: Complex, may violate ToS

**Option D: Different Android Environment**
- Waydroid (container-based, different network stack)
- Genymotion Cloud (different infrastructure)
- Actual physical tablet (user preference needed)

---

## Navigation Quick Reference (dp coordinates)

**Screen Resolution**: 320x640 dp

### Launch to Camera Live View
```bash
# 1. Launch app
adb shell am start -n com.tplink.iot/.view.welcome.StartupActivity

# 2. Wait for home screen
sleep 3

# 3. Tap camera card [16,160][154,280]
adb shell input tap 85 220

# 4. Wait for camera-live
sleep 3
```

### Key Coordinates (320x640 dp)
| Action | Tap Point | Notes |
|--------|-----------|-------|
| Camera card (home) | tap 85 220 | Opens live view |
| Back button | tap 24 57 | Returns to home |
| Fullscreen | tap 252 244 | Landscape mode |
| Pan & Tilt | tap 160 391 | Opens PTZ controls |
| Take Photo | tap 50 302 | Capture snapshot |

---

## Success Criteria
Video feed successfully streams to computer via ONE of:
1. Direct RTSP/ONVIF connection
2. Emulator with working MQTT
3. Periodic screenshot/thumbnail capture
4. Browser-based viewing

---

## Integration Architecture (Post-Fix)

Once video works, the integration with other components:

```
┌─────────────────────────────────────────────────────────────┐
│                   Claude Agent SDK                           │
│  (Orchestrator - coordinates all components)                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬─────────────┐
    │             │             │             │             │
    ▼             ▼             ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Voice   │ │ Camera  │ │ Browser │ │Shopping │ │Datalake │
│ Gateway │ │ Monitor │ │ UI Agent│ │ Agent   │ │(storage)│
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
     │           │           │           │           │
     │           │           │           │           │
 AssemblyAI   Tapo C210   Playwright  Amazon/    SQLite+
              + USB cam              Swiggy      Files
```

**Example Flow**: "Order milk if the fridge is empty"
1. Voice input → omarchy-voice-typing → "order milk if fridge is empty"
2. Claude Agent interprets intent
3. Camera feed → LLM vision analysis → "fridge appears empty"
4. Shopping Agent → Add milk to cart
5. Datalake → Log event with timestamp and screenshot

---

## Next Immediate Actions
1. **Check Tapo app settings** for "Third-Party Compatibility" / RTSP
2. **Scan camera ports** (554, 2020, 443, 80)
3. **If ports open**: Test RTSP with VLC → Problem solved
4. **If ports closed**: Deep-dive into emulator MQTT logs
5. **Document navigation flow** to avoid future tap coordinate confusion
