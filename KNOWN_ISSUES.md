# Known Issues - TAPO C210 Monitor Project

## ~~RESOLVED: Android Emulator Instability~~

**Status: FIXED (2026-01-09)**

### Solution Applied
- Enabled **KVM hardware acceleration** with RTX 2060 SUPER GPU
- Switched from `swiftshader_indirect` to hardware GPU rendering
- System image: `android-34;google_apis_playstore;x86_64`

### Current Working Setup
- AVD Name: `tapo_playstore`
- GPU: Hardware (KVM + RTX 2060 SUPER)
- ARM Translation: `libndk_translation.so` for ARM APKs
- Stability: Good for extended automation sessions

### Original Problem (for reference)
The emulator previously crashed frequently with swiftshader_indirect software rendering.
Root cause was lack of hardware acceleration.

---

## App Installation Challenges

### Problem
Installing Tapo app is complex because:
1. Play Store requires Google account sign-in
2. Aurora Store anonymous mode keeps timing out/crashing
3. Tapo uses App Bundles (split APKs), not universal APK

### Solutions to Explore
1. **apkeep**: Download APKs directly from Play Store
   ```bash
   pip install apkeep
   apkeep -a com.tplink.iot
   ```

2. **SAI (Split APKs Installer)**: Install split APKs on device
   ```bash
   adb install-multiple base.apk split_config.*.apk
   ```

3. **bundletool**: Extract APKs from App Bundle
   ```bash
   bundletool build-apks --bundle=app.aab --output=app.apks
   bundletool install-apks --apks=app.apks
   ```

4. **Direct APK mirror sites**: APKMirror, APKPure (may have universal APKs)

---

## Camera Status

### Current State
- Camera IP: 192.168.29.137
- Status: Not responding ("No route to host")
- Likely needs initial setup via Tapo mobile app

### Ports Checked (all unresponsive)
- 554 (RTSP)
- 443 (HTTPS)
- 80 (HTTP)
- 2020 (Tapo API)
