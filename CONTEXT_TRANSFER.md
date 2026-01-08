# Continue: TAPO C210 Intelligent Monitoring System

**Paste everything below the line in a new Claude Code session from `~/Programs/tapo-c210-monitor`:**

---

## The Story So Far

I'm building an intelligent, LLM-powered monitoring system for my TP-Link TAPO C210 WiFi camera. Here's where we are:

### Chapter 1: The Beginning
I wanted full API control of my TAPO C210 camera. We discovered that while `pytapo` library exists for direct camera API access (RTSP streaming, PTZ control), the camera needs initial setup through the Tapo mobile app first. The camera is on my network at `192.168.29.137` but ports aren't responding yet because it hasn't been configured.

### Chapter 2: The Project Scaffold
We built a complete project at `~/Programs/tapo-c210-monitor` with:

**Direct Camera Control:**
- `src/tapo_c210_monitor/camera.py` - pytapo wrapper for camera API
- `src/tapo_c210_monitor/stream.py` - RTSP stream capture with OpenCV
- `src/tapo_c210_monitor/sync.py` - SD card recording sync

**Android Automation (for Tapo app control):**
- `src/tapo_c210_monitor/android/controller.py` - ADB device control (tap, swipe, text input, screenshots)
- `src/tapo_c210_monitor/android/screen.py` - Screen capture + OCR
- `src/tapo_c210_monitor/android/intelligent_screen.py` - LLM-powered UI element detection
- `src/tapo_c210_monitor/android/ui.py` - High-level UI automation
- `src/tapo_c210_monitor/android/tapo_automator.py` - Tapo app automation
- `src/tapo_c210_monitor/android/file_transfer.py` - Android file sync

**LLM Vision:**
- `src/tapo_c210_monitor/vision/llm_vision.py` - OpenRouter API for screen analysis (GPT-4o-mini, Claude, Gemini)

### Chapter 3: Android Emulator Setup
Since I didn't have a physical phone with USB debugging ready, we set up an Android emulator:

1. Installed Android Studio at `~/Programs/android-studio-local`
2. Set up Android SDK at `~/Android/Sdk`
3. Created emulator `tapo_playstore` with Android 13 + Google Play Store
4. The emulator is working and Play Store is accessible

### Chapter 4: The APK Installation Saga
Installing the Tapo app proved tricky:
- Play Store kept asking for sign-in repeatedly (emulator account persistence issue)
- Direct APK install failed (Tapo uses split APKs, needs bundle installer)
- Downloaded and installed **Aurora Store** (open-source Play Store alternative)

### Chapter 5: Where We Crashed (Current State)
We were in Aurora Store's setup wizard, granting permissions:
1. Successfully launched Aurora Store
2. Got past the initial screen
3. Were on the **permissions screen** granting "Installer Permission"
4. Had to toggle the system permission switch

**THE CRASH:** The session accumulated too many screenshots (42 images at 1080x2400), exceeding Claude's API limit for multi-image requests. The conversation became unrecoverable.

---

## What Needs to Happen Next

### Immediate Task: Complete Aurora Store Setup
1. Check if emulator is still running: `adb devices`
2. If not, start it: `~/Android/Sdk/emulator/emulator -avd tapo_playstore &`
3. Launch Aurora Store: `adb shell am start -n com.aurora.store/.MainActivity`
4. Complete the permission setup wizard
5. Search for "TP-Link Tapo" and install the app

### After Tapo App is Installed
1. Launch Tapo app and go through camera setup
2. Add camera at `192.168.29.137` to my TP-Link account
3. Configure camera settings (enable RTSP, set camera account credentials)
4. Test direct API access using `pytapo`

### Important Technical Notes
- **Screenshot Size Fix:** The `controller.py` has been updated to auto-resize screenshots to max 1900px (under the 2000px API limit). This prevents future crashes.
- **Use UI Automator:** Prefer `adb shell uiautomator dump` to get element bounds instead of repeated screenshot analysis
- **LLM Vision Available:** For complex UI, use `intelligent_screen.py` which calls OpenRouter API (set `OPENROUTER_API_KEY` in `.env`)

---

## Key Commands Reference

```bash
# Check emulator
adb devices

# Start emulator
~/Android/Sdk/emulator/emulator -avd tapo_playstore &

# Take screenshot (auto-resizes to 1900px max)
adb exec-out screencap -p > /tmp/screen.png

# Get UI element positions
adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml /tmp/

# Tap at coordinates
adb shell input tap X Y

# Launch Aurora Store
adb shell am start -n com.aurora.store/.MainActivity

# Launch Tapo (after installed)
adb shell am start -n com.tplink.iot/.MainActivity
```

---

## Resume From Here
Please check the emulator status and continue from where we left off - completing Aurora Store setup and installing the Tapo app. Use the existing modules in this project for Android control. Remember to resize screenshots before reading them to avoid hitting API limits again.
