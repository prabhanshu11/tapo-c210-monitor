# Known Issues - TAPO C210 Monitor Project

## HIGH PRIORITY: Android Emulator Instability

### Problem
The Android emulator (`tapo_playstore` AVD) crashes frequently during operation, typically after:
- Taking screenshots
- Running UI automation commands
- Network operations (like Aurora Store anonymous login)

### Environment
- Emulator: Android 33 (google_apis_playstore, x86_64)
- GPU: swiftshader_indirect
- Host: Linux 6.17.9-arch1-1
- SDK Path: ~/Android/Sdk

### Symptoms
- ADB connection drops ("no devices/emulators found")
- Emulator process terminates without clear error
- qemu process disappears

### Attempted Mitigations (unsuccessful)
- `-no-snapshot` flag
- `-no-boot-anim` flag
- `-no-window` (headless mode)
- `-memory 2048`
- `-gpu swiftshader_indirect`
- `-no-audio`

### Root Cause (suspected)
- Possible memory/resource issues with swiftshader on this system
- May need hardware GPU acceleration (KVM/HAXM)
- Could be filesystem-related (noted: "File System is not ext4, disable QuickbootFileBacked feature")

### Workarounds to Try
1. Use physical Android device with USB debugging
2. Use cloud-based Android (Firebase Test Lab, AWS Device Farm, Genymotion Cloud)
3. Try older Android API level (less resource intensive)
4. Enable KVM acceleration if available

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
