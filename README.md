# TAPO C210 Monitor

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ████████╗ █████╗ ██████╗  ██████╗      ██████╗██████╗  ██╗ ██████╗          ║
║   ╚══██╔══╝██╔══██╗██╔══██╗██╔═══██╗    ██╔════╝╚════██╗███║██╔═████╗         ║
║      ██║   ███████║██████╔╝██║   ██║    ██║      █████╔╝╚██║██║██╔██║         ║
║      ██║   ██╔══██║██╔═══╝ ██║   ██║    ██║     ██╔═══╝  ██║████╔╝██║         ║
║      ██║   ██║  ██║██║     ╚██████╔╝    ╚██████╗███████╗ ██║╚██████╔╝         ║
║      ╚═╝   ╚═╝  ╚═╝╚═╝      ╚═════╝      ╚═════╝╚══════╝ ╚═╝ ╚═════╝          ║
║                                                                               ║
║                    🎥 Intelligent Camera Monitor 🎥                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

AI-powered monitoring system for TP-Link TAPO C210 WiFi camera with **direct RTSP streaming** and **Android automation** for PAN/TILT control.

## ✅ Status: RTSP Working!

```
┌─────────────────────────────────────────────────────────────────┐
│                      RTSP STREAMING ACTIVE                       │
│                                                                 │
│   Camera ────────► RTSP ────────► Your Computer                 │
│   192.168.29.183   Port 554      ffmpeg/VLC/Python              │
│                                                                 │
│   Resolution: 2304x1296 HD │ Codec: H.264 │ FPS: 25             │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Pan Control Experiment                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [RTSP Stream]                [Android Emulator]               │
│   Direct Video                 PAN/TILT Control                 │
│        │                              │                         │
│        ▼                              ▼                         │
│   ┌─────────┐                  ┌─────────────┐                  │
│   │ ffmpeg  │                  │  Tapo App   │                  │
│   │ frame   │                  │  ADB taps   │                  │
│   │ capture │                  │             │                  │
│   └────┬────┘                  └──────┬──────┘                  │
│        │                              │                         │
│        └──────────────┬───────────────┘                         │
│                       ▼                                         │
│        ┌─────────────────────────────────┐                      │
│        │    Visual Change Detection       │                      │
│        │  (Compare frames before/after)   │                      │
│        └─────────────────────────────────┘                      │
│                       │                                         │
│                       ▼                                         │
│        ┌─────────────────────────────────┐                      │
│        │      Claude Agent SDK            │                      │
│        │   (Interpret & Take Actions)     │                      │
│        └─────────────────────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📸 Screenshots

| Home Screen | PTZ Controls |
|-------------|--------------|
| ![Home](ui-exploration/screenshots/camera-offline-home-screen.png) | ![PTZ](ui-exploration/screenshots/camera-live-ptz-panel-open.png) |

## 🚀 Quick Start

### 1. Mobile App Setup (Required First!)

Open the **Tapo app** on your phone and follow these steps:

```
┌─────────────────────────────────────────────────────────────────┐
│                    📱 MOBILE APP SETUP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STEP 1: Enable Third-Party Compatibility                       │
│  ─────────────────────────────────────────                      │
│  📍 Me tab → Settings (gear icon) → Third-Party Compatibility   │
│  ✅ Toggle ON                                                   │
│  ⚠️  Accept the privacy warning dialog                          │
│                                                                 │
│  STEP 2: Create Camera Account (RTSP credentials)               │
│  ─────────────────────────────────────────────────              │
│  📍 Home → Tap camera → Settings (gear) → Advanced Settings     │
│     → Camera Account                                            │
│  ✅ Create username and password                                │
│  💡 This is DIFFERENT from your TP-Link account!                │
│                                                                 │
│  STEP 3: Reboot Camera                                          │
│  ─────────────────────                                          │
│  🔌 Physically unplug and replug the camera                     │
│  ⏱️  Wait 30 seconds for it to reconnect                        │
│  ✅ Ports will now be open (554, 2020, 443, 8800)               │
│                                                                 │
│  STEP 4: Note Your Camera IP                                    │
│  ──────────────────────────                                     │
│  📍 Camera Settings → Device Info → IP Address                  │
│  💡 Or run: ./scripts/discover_camera.sh                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Visual Guide:**

| Step | Screenshot |
|------|------------|
| Third-Party Compatibility | ![Third-Party](ui-exploration/screenshots/2026-01-11-discoveries/01-third-party-compatibility-off.png) |
| Camera Account Warning | ![Warning](ui-exploration/screenshots/2026-01-11-discoveries/07-camera-account-setup-warning.jpg) |

### 2. Discover Camera IP

```bash
./scripts/discover_camera.sh
# Output: 192.168.29.183
```

### 3. Test RTSP Stream

```bash
# Capture a frame
ffmpeg -rtsp_transport tcp \
  -i "rtsp://prabhanshu:iamapantar@192.168.29.183/stream1" \
  -frames:v 1 -update 1 /tmp/frame.jpg

# View with VLC
vlc "rtsp://prabhanshu:iamapantar@192.168.29.183/stream1"
```

## 📡 Network Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 443 | HTTPS | Camera control API |
| 554 | RTSP | Video streaming |
| 2020 | ONVIF | Motion detection |
| 8800 | Proprietary | TP-Link binary protocol |

## 🔧 Features

### Working ✅
- **RTSP video streaming** - Direct HD/SD access
- **Camera discovery** - Auto-find camera on network
- **PAN/TILT controls** - Via Android emulator
- **Photo/video capture** - Via emulator
- **UI automation** - Full Tapo app control

### Emulator Quirks ⚠️
- Video feed blacks out (MQTT issue) - Use RTSP instead
- ANR on live view - Use Me tab for playback access
- PAG library causes main thread blocking

## 🛠️ Installation

```bash
# Clone
git clone https://github.com/prabhanshu11/tapo-c210-monitor.git
cd tapo-c210-monitor

# Install dependencies
uv sync

# Configure
cp .env.example .env
# Edit with your camera details
```

## 📋 Configuration

```bash
# .env file
TAPO_HOST=192.168.29.183
TAPO_USERNAME=prabhanshu
TAPO_PASSWORD=iamapantar
```

## 🌐 Web UI Setup

Launch the configuration web interface:

```bash
uv run python -m tapo_c210_monitor.webui.app
# Open http://localhost:8080
```

The web UI provides:
- Step-by-step mobile app setup checklist
- Camera credential input
- Auto-discovery of camera on network
- RTSP connection testing
- Configuration file generation

## 🎮 Usage

### Python Discovery

```python
from tapo_c210_monitor.discovery import discover_camera, get_rtsp_url

# Find camera
camera_ip = discover_camera()
print(f"Found: {camera_ip}")

# Get RTSP URL
url = get_rtsp_url(camera_ip)
print(f"RTSP: {url}")
```

### CLI Commands

```bash
# Test camera connection
uv run python main.py test-camera

# Take snapshot
uv run python main.py snapshot --output capture.jpg

# Sync recordings
uv run python main.py sync --days 7
```

### Android Emulator Control

```bash
# Start emulator
~/Android/Sdk/emulator/emulator -avd tapo_playstore -gpu host

# Launch Tapo app
adb shell am start -n com.tplink.iot/.view.welcome.StartupActivity

# Navigate to camera (dp coordinates)
adb shell input tap 85 220

# PAN left
adb shell input tap 108 592
```

## 📁 Project Structure

```
tapo-c210-monitor/
├── src/tapo_c210_monitor/
│   ├── discovery.py          # Camera IP discovery
│   ├── android/
│   │   ├── controller.py     # ADB wrapper
│   │   ├── camera_controls.py # PTZ coordinates
│   │   └── tapo_automator.py # UI automation
│   └── vision/
│       └── llm_vision.py     # OpenRouter vision API
├── scripts/
│   └── discover_camera.sh    # Network scanner
├── docs/
│   └── TAPO_APP_INTERNALS.md # How Tapo app works
├── ui-exploration/
│   ├── screens/              # UI documentation
│   ├── screenshots/          # Reference images
│   └── NAVIGATION_QUICK_REF.md
└── README.md
```

## 📖 Documentation

- **[TAPO_APP_INTERNALS.md](docs/TAPO_APP_INTERNALS.md)** - How the Tapo app works internally
- **[CONVERSATION_HISTORY.md](CONVERSATION_HISTORY.md)** - Project development timeline
- **[NAVIGATION_QUICK_REF.md](ui-exploration/NAVIGATION_QUICK_REF.md)** - UI tap coordinates
- **[SESSION_2026-01-11.md](ui-exploration/SESSION_2026-01-11.md)** - Breakthrough session notes

## 🔬 Key Discoveries

1. **MQTT is the video bottleneck** - App uses MQTT via cloud, fails on emulator
2. **RTSP bypasses this** - Direct local access works perfectly
3. **Three steps for RTSP** - Toggle + Account + Reboot (all required!)
4. **PAG causes ANR** - Tencent animation library blocks main thread
5. **Two auth systems** - Cloud (TP-Link) vs Local (Camera Account)

## 🎯 Roadmap

- [x] RTSP streaming
- [x] Camera discovery
- [x] PAN/TILT control via emulator
- [ ] Visual change detection
- [ ] Claude Agent SDK integration
- [ ] Gas knob monitoring experiment
- [ ] Multi-camera support

## 📚 References

- [pytapo](https://github.com/JurajNyiri/pytapo) - Python library for Tapo cameras
- [HomeAssistant-Tapo-Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control) - HA integration
- [TP-Link RTSP FAQ](https://www.tp-link.com/us/support/faq/2680/)

---

<p align="center">
  <i>Built for the intelligent home automation vision</i><br>
  <code>omarchy-voice-typing</code> + <code>tapo-c210-monitor</code> + <code>Claude Agent SDK</code>
</p>
