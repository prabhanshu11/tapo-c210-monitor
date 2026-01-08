# TAPO C210 Monitor

Intelligent monitoring system for TP-Link TAPO C210 WiFi camera with dual control methods:
1. **Direct API** - Using pytapo library for RTSP streaming and camera control
2. **Android Automation** - Control camera via Tapo app using ADB + screen capture + OCR

## Features

- Live RTSP video streaming (HD/SD)
- PTZ (Pan-Tilt-Zoom) camera control
- SD card recording synchronization
- Privacy mode, LED, motion detection control
- Android app automation with simulated touch/keyboard
- Screen capture and OCR for intelligent UI interaction
- File transfer from Android sandbox
- GUI control panel with real-time preview

## Prerequisites

### System Packages (Arch Linux)

```bash
# ADB tools for Android control
sudo pacman -S android-tools

# Tesseract for OCR (optional)
sudo pacman -S tesseract tesseract-data-eng

# FFmpeg (usually already installed)
sudo pacman -S ffmpeg
```

### Camera Setup

1. Install Tapo app on your phone
2. Set up camera and connect to WiFi
3. Create a **Camera Account** (Settings > Advanced Settings > Camera Account)
4. Note the camera IP address

## Installation

```bash
cd ~/Programs/tapo-c210-monitor
uv sync
```

## Configuration

Create a `.env` file:

```bash
cp .env.example .env
# Edit with your camera details
```

Required variables:
- `TAPO_HOST` - Camera IP address
- `TAPO_USERNAME` - Camera account username
- `TAPO_PASSWORD` - Camera account password

Optional:
- `TPLINK_CLOUD_PASSWORD` - TP-Link cloud password (fallback auth)
- `RECORDINGS_OUTPUT_DIR` - Directory for synced recordings

## Usage

### GUI Control Panel

```bash
uv run python main.py gui
```

### Test Connections

```bash
# Test camera API connection
uv run python main.py test-camera

# Test Android ADB connection
uv run python main.py test-android
```

### Sync Recordings

```bash
# Sync today's recordings
uv run python main.py sync

# Sync last 7 days
uv run python main.py sync --days 7 --output ./recordings
```

### Take Snapshot

```bash
uv run python main.py snapshot --output capture.jpg
```

### Watch Android for New Files

```bash
uv run python main.py watch-android --output ./synced
```

### Show System Info

```bash
uv run python main.py info
```

## Android Setup

To use Android automation features:

1. Enable Developer Options on Android device
2. Enable USB Debugging
3. Connect via USB or set up ADB over WiFi:
   ```bash
   adb tcpip 5555
   adb connect <phone-ip>:5555
   ```
4. Install Tapo app on the Android device

## RTSP Stream URLs

Once configured, the camera provides:
- **HD Stream**: `rtsp://<user>:<pass>@<ip>:554/stream1`
- **SD Stream**: `rtsp://<user>:<pass>@<ip>:554/stream2`
- **ONVIF**: `http://<ip>:2020/onvif/device_service`

## Project Structure

```
tapo-c210-monitor/
├── main.py                 # CLI entry point
├── src/tapo_c210_monitor/
│   ├── camera.py           # Direct camera API (pytapo)
│   ├── stream.py           # RTSP stream capture
│   ├── sync.py             # Recording synchronization
│   ├── android/
│   │   ├── controller.py   # ADB device control
│   │   ├── screen.py       # Screen capture + OCR
│   │   ├── ui.py           # UI automation
│   │   └── file_transfer.py # Android file sync
│   └── gui/
│       └── control_panel.py # Tkinter GUI
├── .env.example            # Configuration template
├── pyproject.toml          # Project dependencies
└── README.md
```

## Troubleshooting

### Camera Connection Fails

1. Verify camera IP is correct and reachable (`ping <ip>`)
2. Check camera account credentials in Tapo app
3. Try `admin` as username with TP-Link cloud password
4. Enable "Third-Party Compatibility" in Tapo app (Settings > Tapo Lab)

### Android Connection Fails

1. Run `adb devices` to check connection
2. Accept USB debugging prompt on phone
3. For wireless: `adb connect <ip>:5555`

### RTSP Stream Not Working

1. Test with VLC: `vlc rtsp://<user>:<pass>@<ip>:554/stream1`
2. Check camera firmware is up to date
3. Some models require enabling RTSP in Tapo app settings

## References

- [pytapo](https://github.com/JurajNyiri/pytapo) - Python library for Tapo cameras
- [python-kasa](https://github.com/python-kasa/python-kasa) - TP-Link smart device library
- [TP-Link RTSP/ONVIF FAQ](https://www.tp-link.com/us/support/faq/2680/)
