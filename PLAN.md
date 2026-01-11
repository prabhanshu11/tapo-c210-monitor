# Plan: Tapo C210 Integration

## The Broader Vision

You're building an **intelligent home automation system** with multiple components:

| Component | Purpose | Status |
|-----------|---------|--------|
| **omarchy-voice-typing** | Voice input via AssemblyAI | ✅ Working |
| **datalake** | Data storage (audio, transcripts, screenshots) | ✅ Working |
| **UI-agent** | Browser automation (PPE loop) | ✅ Working |
| **shopping-agent** | Multi-platform shopping | 🔄 In progress |
| **usb-webcam-api** | USB camera streaming | ✅ Working |
| **tapo-c210-monitor** | WiFi camera integration | ✅ **WORKING** |

---

## Current Capabilities (2026-01-11)

### ✅ Video Streaming (RTSP)
```bash
# HD stream (2304x1296)
ffplay rtsp://username:password@192.168.29.183/stream1

# SD stream
ffplay rtsp://username:password@192.168.29.183/stream2
```

### ✅ PTZ Control (ONVIF)
```python
from tapo_c210_monitor.ptz_mapper import ONVIFPTZController

ctrl = ONVIFPTZController()
ctrl.connect()

# Absolute positioning (-1.0 to 1.0)
ctrl.move_absolute(pan=0.5, tilt=0.0)

# Get current position
pos = ctrl.get_position()  # Returns PTZPosition(pan, tilt, zoom)

# Convenience methods
ctrl.pan_left(duration=1.0)
ctrl.pan_right(duration=1.0)
ctrl.tilt_up(duration=1.0)
ctrl.tilt_down(duration=1.0)
```

### ✅ Position Feedback
- Real-time position via ONVIF GetStatus
- Pan: -1.0 (left) to 1.0 (right)
- Tilt: -1.0 (down) to 1.0 (up)

### ❌ What Doesn't Work
- **Android emulator approach** - ANR blocks live view, PTZ controls inaccessible
- **pytapo library** - Requires cloud password, not camera account credentials
- **GotoHome** - Not supported by this camera model

---

## Prerequisites (One-Time Setup)

1. **Enable Third-Party Compatibility** in Tapo app (Me → Settings)
2. **Create Camera Account** (Camera Settings → Advanced → Camera Account)
3. **Reboot camera** (power cycle after enabling)
4. **Set static IP** (recommended for reliability)

---

## Integration Architecture

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
              (RTSP+ONVIF)            Swiggy      Files
```

---

## Next Steps

### Phase 1: Core Monitoring
- [ ] Frame capture from RTSP stream
- [ ] Motion detection (compare frames)
- [ ] LLM vision analysis (describe what camera sees)
- [ ] Event logging to datalake

### Phase 2: Voice Integration
- [ ] "Look at the front door" → Pan to preset position
- [ ] "What do you see?" → Capture frame → LLM description
- [ ] "Is anyone home?" → Detect presence via motion/LLM

### Phase 3: Automation
- [ ] Presence-based actions (lights, notifications)
- [ ] Scheduled patrol patterns
- [ ] Anomaly detection alerts

---

## Technical Reference

### Ports Used
| Port | Protocol | Purpose |
|------|----------|---------|
| 554 | RTSP | Video streaming |
| 2020 | ONVIF | PTZ control, device info |
| 443 | HTTPS | Web interface |
| 8800 | Proprietary | TP-Link internal |

### Key Files
- `src/tapo_c210_monitor/ptz_mapper/` - ONVIF PTZ controller
- `src/tapo_c210_monitor/discovery.py` - Camera discovery
- `src/tapo_c210_monitor/experiments/` - Visual change detection
- `.env` - Credentials (not committed)

### Environment Variables
```
TAPO_HOST=192.168.29.183
TAPO_USERNAME=your_camera_account
TAPO_PASSWORD=your_camera_password
```
