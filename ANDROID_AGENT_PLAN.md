# Android Automation Agent - Engineering Plan

## Mission Statement
Build a robust, self-healing Android automation agent that combines UX simulation with ADB commands, capable of reliably installing apps and interacting with Android devices.

---

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Android Automation Agent                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Session    │  │   Device     │  │    Event     │          │
│  │   Manager    │  │   Monitor    │  │    Logger    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                  │                   │
│         └─────────────────┼──────────────────┘                   │
│                           │                                      │
│  ┌────────────────────────┴────────────────────────┐            │
│  │              Core Controller                      │            │
│  │  - Emulator lifecycle management                  │            │
│  │  - ADB command execution with retry               │            │
│  │  - State machine for operations                   │            │
│  └──────────────────────────────────────────────────┘            │
│                           │                                      │
│  ┌────────────┬───────────┴───────────┬────────────┐            │
│  │            │                       │            │            │
│  ▼            ▼                       ▼            ▼            │
│ ┌────┐    ┌────────┐           ┌──────────┐  ┌─────────┐       │
│ │ADB │    │   UI   │           │   App    │  │ Screen  │       │
│ │Cmds│    │Automator│          │Installer │  │ Reader  │       │
│ └────┘    └────────┘           └──────────┘  └─────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

#### 1. Session Manager (`session_manager.py`)
- Start/stop sessions with unique IDs
- Create session directories for logs
- Generate session summaries on completion
- Track session state and metrics

#### 2. Device Monitor (`device_monitor.py`)
- Continuous health checks via ADB
- Detect disconnections immediately
- Auto-restart emulator on crash
- Track device state transitions

#### 3. Event Logger (`event_logger.py`)
- Structured JSON logging for all events
- Screenshot archival with timestamps
- UI hierarchy dumps
- Error and crash logging

#### 4. Core Controller (`controller.py`)
- Central orchestration
- Retry logic with exponential backoff
- Operation queuing
- State machine management

#### 5. UI Automator (`ui_automator.py`)
- Parse UI hierarchy XML
- Find elements by text, resource-id, class
- Calculate tap coordinates
- Handle scrolling and gestures

#### 6. App Installer (`app_installer.py`)
- Multiple installation methods:
  - Direct APK via `adb install`
  - Split APKs via `adb install-multiple`
  - Via Aurora Store (anonymous)
  - Via Play Store (with account)
  - Download from APK mirrors
- Verify installation success

#### 7. Screen Reader (`screen_reader.py`)
- Efficient UI state detection
- Minimize screenshot usage
- Cache UI hierarchies
- OCR fallback for complex UIs

---

## Key Design Decisions

### 1. Prefer ADB Commands Over Screenshots
- UI hierarchy dumps (uiautomator) are lightweight
- Screenshots should be last resort (high token cost)
- Cache and reuse UI state when possible

### 2. Robust Error Handling
```python
class RetryStrategy:
    MAX_RETRIES = 3
    BACKOFF_BASE = 2  # seconds

    @staticmethod
    def execute_with_retry(operation, *args):
        for attempt in range(MAX_RETRIES):
            try:
                return operation(*args)
            except DeviceDisconnectedError:
                wait_time = BACKOFF_BASE ** attempt
                log_retry(attempt, wait_time)
                reconnect_device()
                time.sleep(wait_time)
        raise MaxRetriesExceeded()
```

### 3. State Machine for Operations
```
States:
  IDLE -> CONNECTING -> READY -> OPERATING -> COMPLETING -> IDLE
                 ↓          ↓           ↓
              ERROR <──────┴───────────┘
                 ↓
            RECOVERING -> READY (or FAILED)
```

### 4. Session-Based Logging
```
sessions/
  └── 2024-01-08_17-30-00_install-tapo/
      ├── session.json       # Metadata
      ├── events.jsonl       # Event stream
      ├── screenshots/       # Only when needed
      │   ├── 001_initial.png
      │   └── 002_error.png
      ├── ui_dumps/          # UI hierarchies
      │   ├── 001.xml
      │   └── 002.xml
      └── summary.md         # Auto-generated summary
```

---

## Installation Strategies

### Strategy Priority Order

1. **Direct APK Install** (fastest, most reliable)
   - Check APK mirrors (APKMirror, APKPure)
   - Use apkeep for Play Store download
   - `adb install app.apk`

2. **Split APK Install** (for App Bundles)
   - Download all splits
   - `adb install-multiple base.apk config.*.apk`

3. **Aurora Store Anonymous** (no account needed)
   - Grant permissions via ADB
   - Use market intents for direct navigation
   - Handle session refresh automatically

4. **Play Store** (requires account)
   - Last resort
   - Requires Google account setup

### APK Sources to Implement

```python
APK_SOURCES = [
    APKMirrorSource(),      # apkmirror.com
    APKPureSource(),        # apkpure.com
    APKComboSource(),       # apkcombo.com
    ApkeepSource(),         # Direct Play Store download
    AuroraStoreSource(),    # Via Aurora Store app
]
```

---

## Emulator Stability Solutions

### Immediate Actions
1. Log all emulator output to file
2. Monitor process with watchdog
3. Auto-restart with clean state on crash

### Configuration to Test
```bash
# Conservative settings
emulator -avd tapo_playstore \
  -memory 2048 \
  -cores 2 \
  -gpu swiftshader_indirect \
  -no-snapshot \
  -no-boot-anim \
  -no-audio \
  -partition-size 4096

# With KVM (if available)
emulator -avd tapo_playstore \
  -gpu host \
  -accel on
```

### Fallback Options
1. Older Android API (28 instead of 33)
2. ARM instead of x86_64
3. Physical device
4. Cloud Android (Genymotion, Firebase)

---

## Implementation Phases

### Phase 1: Foundation (Current)
- [ ] Create logging infrastructure
- [ ] Implement device monitor with auto-recovery
- [ ] Build session manager
- [ ] Test emulator stability fixes

### Phase 2: UI Automation
- [ ] Build efficient UI element finder
- [ ] Implement common actions (tap, swipe, type)
- [ ] Create action recording/playback
- [ ] Add wait-for-element with timeout

### Phase 3: App Installation
- [ ] Implement APK source adapters
- [ ] Build split APK handler
- [ ] Create Aurora Store automator
- [ ] Add installation verification

### Phase 4: Intelligence
- [ ] Add LLM-based screen understanding
- [ ] Implement adaptive navigation
- [ ] Create error recovery strategies
- [ ] Build test suite

---

## Files to Create

```
src/tapo_c210_monitor/android/
├── __init__.py
├── session_manager.py      # Session lifecycle
├── device_monitor.py       # Device health checks
├── event_logger.py         # Structured logging
├── emulator_manager.py     # Emulator lifecycle
├── ui_automator.py         # UI interactions
├── app_installer.py        # App installation
├── apk_sources/            # APK download sources
│   ├── __init__.py
│   ├── base.py
│   ├── apkmirror.py
│   ├── apkpure.py
│   └── aurora.py
└── utils/
    ├── adb.py              # ADB wrapper with retry
    └── retry.py            # Retry utilities
```

---

## Next Steps

1. Research: Look up Android automation best practices, common pitfalls
2. Implement: Start with event_logger and session_manager
3. Test: Create stability test for emulator
4. Iterate: Fix issues as they appear
