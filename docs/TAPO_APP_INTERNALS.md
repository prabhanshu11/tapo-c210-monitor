# Tapo App Internals

Discoveries about how the TP-Link Tapo app works internally, gathered during the tapo-c210-monitor project (2026-01-11).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Tapo App                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        │
│  │ TP-Link     │     │   MQTT      │     │   HTTP/     │        │
│  │ Cloud Auth  │     │   Client    │     │   REST      │        │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘        │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              TP-Link Cloud Relay                     │        │
│  │         (mqtt-*.tplinkcloud.com)                     │        │
│  └─────────────────────────────────────────────────────┘        │
│                            │                                    │
│                            ▼                                    │
│                    ┌───────────────┐                            │
│                    │  Tapo Camera  │                            │
│                    │   (C210)      │                            │
│                    └───────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Authentication System

### Two Separate Credential Systems

| Credential Type | Purpose | Where to Create |
|-----------------|---------|-----------------|
| **TP-Link Account** | Cloud login, app authentication | tapo.com / app signup |
| **Camera Account** | Local RTSP/ONVIF access | App → Camera Settings → Advanced → Camera Account |

**Important**: Camera Account is REQUIRED for third-party integrations (Home Assistant, VLC, NVR).

### Third-Party Compatibility Feature

**Location**: Me tab → Settings → Third-Party Compatibility

**What it does**:
- Enables local network protocols (RTSP, ONVIF)
- Opens ports 443, 554, 2020, 8800 on camera
- Allows Home Assistant and other platforms to connect

**Requirements to work**:
1. Enable Third-Party Compatibility toggle
2. Create Camera Account (Advanced Settings)
3. **Reboot camera** (power cycle required!)

Without all three steps, ports remain closed.

## Video Streaming Protocols

### Primary: MQTT over Cloud Relay

The Tapo app uses **MQTT protocol via TP-Link cloud** for live video streaming:

```
App ──► TP-Link Cloud (MQTT) ──► Camera
```

**Error when MQTT fails**:
```
MediaException{errorCode=-2016, message='Don't exist mqtt connection!'}
Client is not connected (32104)
```

**Why MQTT fails on Android emulator**:
- Unknown root cause (possibly emulator network stack issues)
- NAT/keepalive handling differences from physical devices
- May be anti-emulator detection

### Secondary: RTSP (Local Network)

When Third-Party Compatibility + Camera Account are configured:

```
App/VLC ──► Camera (direct, port 554)
```

**RTSP URLs**:
- HD: `rtsp://<username>:<password>@<camera_ip>/stream1` (2304x1296)
- SD: `rtsp://<username>:<password>@<camera_ip>/stream2`

### Control Commands: HTTP/REST

PAN/TILT and other controls use **HTTP/REST** (not MQTT):

```
App ──► TP-Link Cloud (HTTPS) ──► Camera
```

**Note**: The app's HTTP control path requires active video connection context - controls don't work independently on emulator.

## Network Ports (When Third-Party Enabled)

| Port | Protocol | Purpose |
|------|----------|---------|
| 443 | HTTPS | Camera control API |
| 554 | RTSP | Video streaming |
| 2020 | ONVIF | Motion detection, PTZ |
| 8800 | Proprietary | TP-Link binary video protocol |
| 80 | HTTP | Not used (closed) |

**Note**: Ports only open after:
1. Third-Party Compatibility enabled
2. Camera Account created
3. Camera rebooted

## UI Components

### PAG Library (libpag.so)

**What**: Portable Animated Graphics library by Tencent

**Used for**:
- Overlay button animations (fade in/out)
- "1/24" camera counter transitions
- UI polish effects in live view

**Problem on emulator**:
```
Thread[1,tid=3796,Native,Thread*=...,"main"] recursive attempt to load library
"/data/app/.../libpag.so"
I/Choreographer: Skipped 44 frames! The application may be doing too much work on its main thread.
```

**Impact**:
- 140-180% CPU usage on emulator
- ANR (App Not Responding) dialogs
- Main thread blocking

**Workaround**: Use RTSP instead of in-app video view.

### Activities

| Activity | Screen |
|----------|--------|
| `StartupActivity` | Splash, login, terms |
| `MainActivity` | Home screen with device list |
| `VideoPlayV3Activity` | Camera live view |
| `LoginActivity` | Login form |
| `PaneListCommonActivity` | Camera selection lists |
| `TapoPlaybackAndDownloadActivity` | Recordings library |

## Storage Architecture

### Three Storage Locations

| Location | Access Method | Notes |
|----------|---------------|-------|
| **Phone Storage** | Me → Camera Memory | Photos/videos you capture |
| **SD Card** | Me → Playback & Download | Camera's continuous recording |
| **Tapo Care Cloud** | Me → Playback & Download | Subscription cloud storage |

**Limitation**: Camera hardware can only serve 2 of 3 simultaneously:
- SD Card + Tapo Care = NVR/ONVIF disabled
- SD Card + NVR = Tapo Care disabled
- Remove SD card to enable all external access

## App Navigation Quirks

### ANR-Prone Paths

| Path | Result |
|------|--------|
| Home → Camera Card → Live View | ANR on emulator |
| Live View → Playback & Download | ANR on emulator |
| Live View → Fullscreen | ANR on emulator |

### Working Paths (on Emulator)

| Path | Result |
|------|--------|
| Home → Me → Playback & Download | Works |
| Home → Me → Camera Memory | Works |
| Home → Me → Settings | Works |

**Note**: Live camera view causes ANR, making app-based PTZ control unreliable on emulator.

## Coordinate System

**Physical pixels**: 720x1280 (device screen)
**Logical coordinates**: 320x640 dp (uiautomator, adb input tap)

```bash
# CORRECT - use dp coordinates
adb shell input tap 160 603

# WRONG - physical pixels won't work
adb shell input tap 360 1206
```

## Discovered via Reverse Engineering

### MQTT Broker
- Hostname pattern: `mqtt-*.tplinkcloud.com`
- Uses TLS encryption
- Device-specific topics

### Cloud API
- Base: `https://wap.tplinkcloud.com`
- Authentication: Bearer token from TP-Link login
- Device control via JSON-RPC style calls

### Local API (when enabled)
- ONVIF standard compliance
- RTSP with H.264/H.265
- Basic auth with Camera Account credentials

## Camera Connectivity Issue (2026-01-11) - NEEDS INVESTIGATION

**Observed**: Camera ports (443, 554, 2020, 8800) sometimes stop responding to scans.

**Possible causes to investigate**:
- Network connectivity issue (WiFi dropout)
- Router/firewall behavior
- DHCP lease changes when IP changed from dynamic to static
- Unknown camera behavior (Tapo cameras typically stay online continuously)

**What seemed to help**:
- Opening camera view in phone app
- Setting static IP in camera settings

**Note**: User reports Tapo cameras normally don't sleep - this behavior is unusual and needs investigation.

**TODO**:
- Check router logs during connectivity loss
- Review SD card diagnostic logs for clues
- Test if RTSP keepalive prevents the issue

## Diagnostic Logging (SD Card)

Camera can save diagnostic logs to MicroSD card:

**Location**: Camera Settings → Diagnostics App

**Purpose**: Debug information for potential analysis/hacking to improve:
- Custom firmware possibilities
- Direct API access without cloud
- Sleep mode control
- Commercial integration opportunities

**Status**: Enabled, logs accumulating on SD card.

## Key Findings Summary

1. **MQTT is the bottleneck** - Video streaming relies on MQTT which fails on emulator
2. **RTSP bypasses the problem** - Direct local access avoids cloud relay
3. **Three steps for RTSP** - Toggle + Account + Reboot (all required)
4. **PAG causes ANR** - Animation library blocks main thread
5. **Two auth systems** - Cloud vs Local credentials are different
6. **ONVIF is the solution** - Direct PTZ control via port 2020 works reliably (see `ptz_mapper/README.md`)
7. **App-based PTZ fails on emulator** - ANR blocks the live view screen where PTZ controls live

## References

- Session log: `ui-exploration/SESSION_2026-01-11.md`
- Third-party setup: `ui-exploration/screens/third-party-compatibility.md`
- Navigation coords: `ui-exploration/NAVIGATION_QUICK_REF.md`
- **PTZ Control**: `src/tapo_c210_monitor/ptz_mapper/README.md` - Working ONVIF-based solution
- Home Assistant integration: [HomeAssistant-Tapo-Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control)
