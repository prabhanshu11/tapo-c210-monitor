# Android Emulator Timing Guide

**Purpose:** Avoid wasteful waits in automation scripts.

## Critical Findings (2026-01-11)

**Measured by user:**
- Emulator boot time: **15-18 seconds** (actual)
- App launch time: **immediate** (0-1s)

**Claude's wasteful waits:**
- Emulator wait: **3m45s** (wasted ~3m27s per boot!)
- App launch wait: **1m30s** (wasted ~1m30s per launch!)
- **Total waste: ~5 minutes per automation cycle** 🤦

**Root cause of waste:** Using `sleep` with large timeouts instead of `adb wait-for-device`.

## Emulator Boot Time

**Measured:** 15-18 seconds (with KVM acceleration)

### Optimal Wait Pattern
```bash
# Start emulator in background
~/Android/Sdk/emulator/emulator -avd tapo_playstore -gpu host -no-snapshot -no-audio &

# Wait for device to be ready
adb wait-for-device  # Blocks until device is online

# Brief settle (optional, for boot animation to finish)
sleep 3

# Ready for commands
# Total time: ~18-20 seconds
```

### Common Mistakes
❌ `sleep 25` - Wastes ~10 seconds
❌ `sleep 60` - Wastes ~42 seconds
✅ `adb wait-for-device` - Returns immediately when ready

---

## App Launch Time

**Measured:** Immediate (0-1 second)

### Optimal Launch Pattern
```bash
# Launch app
adb shell am start -n com.tplink.iot/.view.welcome.StartupActivity

# NO WAIT NEEDED - app is already running
# Proceed immediately to next command
```

### Common Mistakes
❌ `sleep 2` after app launch - Wastes 2 seconds
❌ `sleep 3` after app launch - Wastes 3 seconds
✅ No sleep - App is ready immediately

---

## UI Element Wait Pattern

For waiting for specific UI elements (e.g., after navigation):

```bash
# Tap navigation button
adb shell input tap X Y

# For UI state changes, use minimal waits
sleep 0.5  # 500ms for UI transition

# For network requests (login, etc.)
sleep 1    # 1 second max

# Verify state with uiautomator dump instead of blind waiting
adb shell uiautomator dump
```

---

## Timing Summary

| Operation | Actual Time | Recommended Wait | Common Wasteful Wait |
|-----------|-------------|------------------|---------------------|
| Emulator boot | 15-18s | `adb wait-for-device` + 3s | `sleep 25` (+10s waste) |
| App launch | 0-1s | None | `sleep 2-3` (+2-3s waste) |
| UI navigation | 0.3-0.5s | `sleep 0.5` | `sleep 2` (+1.5s waste) |
| Network request | 0.5-1s | `sleep 1` | `sleep 3` (+2s waste) |

**Rule of thumb:** Use `adb wait-for-device` for boot, minimal sleeps (0.5-1s) for UI, verify state instead of blind waiting.
