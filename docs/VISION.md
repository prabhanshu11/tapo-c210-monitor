# Vision & Data Model - Star Trek Computer

## Part 1: Bold Ideas from Session 5fc36dcc (The Vision Session)

### Your Original Statement (Pasted Text)
> "I want to create an **intelligent, modern, LLM-based, inference-powered monitoring system** using my TP-Link Wi-Fi webcam TAPO C210. So I need **full API control of the camera**... we will quickly start with installing Android Studio, installing the TP Link app and then using the app interface to... first connect to the TP Link webcam, capture the live video and also **set up a feed to copy all the video as it is created on the TP Link CCTV camera SD card onto the desktop server.**"

### Bold Ideas Extracted

| # | Bold Idea | Quote | Status |
|---|-----------|-------|--------|
| 1 | **LLM-powered inference monitoring** | "intelligent, modern, LLM-based, inference-powered monitoring system" | ✅ Working (Gemini 3 Flash via OpenRouter) |
| 2 | **Full API control** | "full API control of the camera" | ✅ Working (ONVIF PTZ + RTSP) |
| 3 | **SD card sync** | "copy all the video as it is created on the camera SD card" | 🔄 Scaffolded, not tested |
| 4 | **Robust Android scaffolding** | "scaffolding... to control the app using simulated touch and keyboard and capture its screen, then intelligently move camera" | ✅ Created (32+ screens documented) |
| 5 | **Computer vision via OpenRouter** | "inferring UI elements using an external api like openrouter" | ✅ Working |
| 6 | **Modular cognitive architecture** | "cognitive logic/model can remain in a folder and android specific control has a folder" | ✅ Implemented (src/vision/, src/android/) |
| 7 | **GPU-powered screenshot intelligence** | "good enough gpu for screenshot intelligence" | ✅ Available (RTX 2060 SUPER) |
| 8 | **AI consciousness** | "I'm talking about, fucking creating a AI consciousness here" | 🎯 North Star |
| 9 | **Star Trek computer vision** | "ultimate star trek computer vision" | 🎯 North Star |
| 10 | **Intelligent life & objects tracker** | "ai agent based intelligent life and objects tracker" | 🔄 Foundation laid |
| 11 | **Parallel emulators** | "2 emulators with 2 instances of the app, will allow parallel control + feed view" | 📝 Noted, deferred (RTSP solved video) |
| 12 | **Bootup time optimization** | "constantly trying to make the bootup time of agents/workflows faster" | 🔄 Ongoing |
| 13 | **Gas knob experiment** | "physical actuator integration" | 📋 Next priority |

---

## Part 2: The Data Model

### The Core Insight

You're building **ambient intelligence** - a system that:
1. **Perceives** continuously (cameras, audio, screenshots)
2. **Understands** via LLM (what changed? who's there? is the stove on?)
3. **Acts** when needed (alerts, automation, control)
4. **Learns** from patterns (time-based, entity-based)

### Entity Relationships Across Projects

```
┌─────────────────────────────────────────────────────────────────┐
│                      UNIFIED DATA MODEL                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐                                                │
│  │   SESSION   │ ◄── Which agent, conversation, timestamp       │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        │
│  │   EVENT     │────►│   ENTITY    │◄────│  POSITION   │        │
│  │ (change)    │     │ (camera,    │     │ (pan/tilt,  │        │
│  │             │     │  person,    │     │  location)  │        │
│  │             │     │  object)    │     │             │        │
│  └──────┬──────┘     └─────────────┘     └─────────────┘        │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────────────────────────────────────────────┐        │
│  │                      FRAME                           │        │
│  │  - Unix timestamp                                    │        │
│  │  - Source (camera ID, screen ID, audio device)       │        │
│  │  - File path or blob                                 │        │
│  │  - Metadata (resolution, duration, codec)            │        │
│  └─────────────────────────────────────────────────────┘        │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────┐        │
│  │                   LLM_ANALYSIS                       │        │
│  │  - Unix timestamp                                    │        │
│  │  - Model used                                        │        │
│  │  - Prompt                                            │        │
│  │  - Response                                          │        │
│  │  - Frames referenced (before/after)                  │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data by Project

| Project | What it Produces | Key Fields |
|---------|------------------|------------|
| **tapo-c210-monitor** | Video frames, PTZ positions, change events | `{unix_ts, camera_id, pan, tilt, frame_path, event_type}` |
| **omarchy-voice-typing** | Audio recordings, transcripts | `{unix_ts, audio_path, transcript_text, duration}` |
| **UI-agent** | Screenshots, UI elements, actions | `{unix_ts, screen_id, screenshot_path, elements[], action_taken}` |
| **ring buffer** | Continuous video segments | `{unix_ts_start, unix_ts_end, segment_path, camera_id}` |
| **change detector** | Change events with LLM analysis | `{unix_ts, change_score, frames_before[], frames_after[], llm_response}` |

### Proposed Core Tables

```sql
-- All timestamps are Unix time (seconds since epoch)

CREATE TABLE sessions (
    id TEXT PRIMARY KEY,           -- UUID
    unix_ts_start INTEGER,
    unix_ts_end INTEGER,
    agent_type TEXT,               -- 'tapo-monitor', 'voice-typing', 'ui-agent'
    conversation_id TEXT           -- Claude session ID if applicable
);

CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    entity_type TEXT,              -- 'camera', 'person', 'object', 'screen'
    name TEXT,
    metadata JSON                  -- {ip, credentials, capabilities...}
);

CREATE TABLE frames (
    id TEXT PRIMARY KEY,
    unix_ts INTEGER,
    entity_id TEXT REFERENCES entities(id),
    file_path TEXT,
    frame_type TEXT,               -- 'video_frame', 'screenshot', 'audio'
    metadata JSON                  -- {resolution, codec, duration...}
);

CREATE TABLE events (
    id TEXT PRIMARY KEY,
    unix_ts INTEGER,
    event_type TEXT,               -- 'change_detected', 'voice_command', 'action_taken'
    entity_id TEXT REFERENCES entities(id),
    session_id TEXT REFERENCES sessions(id),
    frames_before JSON,            -- [frame_ids...]
    frames_after JSON,
    metadata JSON
);

CREATE TABLE llm_analyses (
    id TEXT PRIMARY KEY,
    unix_ts INTEGER,
    event_id TEXT REFERENCES events(id),
    model TEXT,                    -- 'google/gemini-3-flash-preview'
    prompt TEXT,
    response TEXT,
    tokens_used INTEGER
);

CREATE TABLE positions (
    id TEXT PRIMARY KEY,
    unix_ts INTEGER,
    entity_id TEXT REFERENCES entities(id),
    pan REAL,
    tilt REAL,
    zoom REAL
);
```

### What This Enables

1. **"Computer, is the stove on?"**
   - Query: Find latest frame from kitchen camera
   - LLM analyze for gas knob position
   - Return natural language answer

2. **"Who came home in the last hour?"**
   - Query: Events where `event_type = 'person_detected'` in time range
   - Return person entities with timestamps

3. **"Show me what happened when the camera moved"**
   - Query: Events with position changes, join with frames
   - Display timeline with before/after

4. **Voice + Vision integration**
   - Voice command → transcript → query entities → camera action → frame capture → LLM analysis → voice response

---

## Part 3: Ideas Extracted from Voice Transcripts (323 transcripts analyzed)

### Category 1: AI Consciousness / Ambient Intelligence
| Idea | Source | Status |
|------|--------|--------|
| **"Create an AI consciousness"** | e2c9ece8 | 🎯 North Star |
| **"Star Trek computer vision"** | e2c9ece8 | 🎯 North Star |
| **"Intelligent home automation system"** | 20260111_044836 | 🔄 Building blocks in place |
| **"Claude Agent SDK + home automation tools"** | 20260111_044936 | 📋 To integrate |
| **"AI agent based intelligent life and objects tracker"** | 20260109_051724 | 🔄 Foundation laid |

### Category 2: Camera & Vision System
| Idea | Source | Status |
|------|--------|--------|
| **Full API control of camera** | 5fc36dcc | ✅ Done (ONVIF + RTSP) |
| **Gas knob experiment** - actuator + camera + web UI | 20260109_051724 | 📋 Next priority |
| **Ring buffer** - 30 min video buffer like gaming | 20260111_064109 | ✅ Implemented (Go) |
| **Visual change detection** - compare frames | Progress_actual | ✅ Working |
| **LLM vision analysis** - describe what changed | change_detector.py | ✅ Working |
| **Multi-camera support** - home monitoring | CONVERSATION_HISTORY | 📋 Future |
| **Camera diagnostic logs** - SD card hacking | 20260111_055654 | 📋 To research |
| **PTZ mapper** - absolute position mapping | 20260111_062546 | ✅ Implemented |

### Category 3: Voice Integration
| Idea | Source | Status |
|------|--------|--------|
| **Voice typing** - Dvorak/Qwerty compatible | omarchy-voice-typing | ✅ Working |
| **"Look at the front door" → Pan to preset** | PLAN.md | 📋 To implement |
| **"What do you see?" → Capture + describe** | PLAN.md | 📋 To implement |
| **"Is anyone home?" → Presence detection** | PLAN.md | 📋 To implement |
| **AssemblyAI transcription** | 20260110_035752 | ✅ Working |

### Category 4: Multi-Agent Architecture
| Idea | Source | Status |
|------|--------|--------|
| **Orchestrator + Worker agents** - parallel UI exploration | 20260109_050208 | ✅ Done |
| **Multi-emulator parallel control** | e2c9ece8 | 📝 Noted, deferred |
| **Sub-agents for specific tasks** | 20260108_165540 | ✅ Using |
| **Claude Code hooks** - inject messages to agents | 20260109_165245 | 📋 To explore |
| **Memory profiler** - freeze runaway agents | 20260109_165245 | 📋 To implement |

### Category 5: Browser/UI Automation
| Idea | Source | Status |
|------|--------|--------|
| **Shopping agent** - Amazon cart, address verification | 20260109_153436 | 🔄 In progress |
| **Sign-in utility** - YubiKey/FIDO2 automation | 20260109_170856 | 📋 To implement |
| **Popup handler** - vision-based cross detection | 20260109_173015 | 📋 To implement |
| **Screenshot logging** - audit trail | 20260109_173015 | 🔄 Partial |
| **UI learnings** - skills for repeated workflows | 20260109_172146 | 📋 To formalize |

### Category 6: System Infrastructure
| Idea | Source | Status |
|------|--------|--------|
| **Local bootstrapping** - reproducible system setup | local-bootstrapping | ✅ Working |
| **Tailscale sync** - desktop/laptop coordination | 20260108_173628 | ✅ Working |
| **Swap expansion** - dynamic SSD swap | 20260109_165245 | ✅ Implemented |
| **Freeze detection** - system hang logging | 20260109_155720 | ✅ Implemented |
| **Waybar widgets** - status indicators | 20260109_163034 | ✅ Working |
| **Sunshine/Moonlight** - remote desktop | 20260108_173628 | 🔄 In progress |

### Category 7: Data & Logging
| Idea | Source | Status |
|------|--------|--------|
| **Unix timestamps everywhere** | CLAUDE.md | ✅ Implemented |
| **JSONL session logs** - NASA engineer approach | agents.md | ✅ Implemented |
| **Transcript storage** - ~/Programs/transcripts | omarchy-voice-typing | ✅ Working (323 files) |
| **Recording storage** - ~/Programs/recordings | omarchy-voice-typing | ✅ Working |
| **Action logging** - audit for shopping agent | 20260109_172306 | 📋 To implement |
| **Web UI for review** - screenshots + errors | 20260109_180218 | 📋 To implement |

### Category 8: Conversation Management
| Idea | Source | Status |
|------|--------|--------|
| **Conversation recall skill** - search past sessions | conversation-recall | ✅ Working |
| **Context transfer** - off-ramp conversations | 20260108_165540 | ✅ CONTEXT_TRANSFER.md |
| **Subagent tracking** - who spawned what | 20260110_025135 | 📋 To implement |
| **Fork detection** - conversation branches | 20260110_025135 | 📋 To implement |
| **HTML export** - with copy buttons | 20260110_184846 | 📋 To implement |

---

## Key Patterns Emerging

### The "Computer, do X" Pattern
Voice command → NLU → Entity lookup → Action → Visual verification → Response

```
User: "Computer, is the stove on?"
  ↓
Voice typing (omarchy-voice-typing)
  ↓
Intent: check_stove_status
  ↓
Entity: kitchen_camera (from entities table)
  ↓
Action: capture_frame(kitchen_camera)
  ↓
LLM Vision: analyze_for("gas knob position")
  ↓
Response: "The gas knob appears to be in the OFF position"
```

### The Continuous Awareness Pattern
Ring buffer → Change detection → LLM analysis → Event storage → Queryable history

```
RTSP Stream → Ring Buffer (30 min)
  ↓
Change Detector (every 2s)
  ↓
If change_score > threshold:
  ↓
  LLM Vision Analysis
  ↓
  Store event with frames
  ↓
Queryable: "What happened at 3pm?"
```

### The Multi-Device Pattern
Desktop ↔ Laptop via Tailscale, unified config via local-bootstrapping

```
Desktop (main workstation)
  ├── Camera monitoring
  ├── Heavy GPU tasks
  └── Emulators

Laptop (mobile/backup)
  ├── 32GB RAM for agents
  ├── Backup processing
  └── Moonlight client

Sync via:
  └── local-bootstrapping repo (git)
  └── Tailscale (network)
```

---

## The Vision: Star Trek Computer Checklist

### Perception Layer
- [x] **Vision** - Camera with LLM understanding
- [x] **Hearing** - Voice typing with AssemblyAI
- [ ] **Touch** - Physical actuators (gas knob experiment)
- [ ] **Presence** - Motion detection + person tracking

### Understanding Layer
- [x] **Scene description** - "What do you see?"
- [x] **Change detection** - "What happened?"
- [ ] **Object tracking** - "Where is my keys?"
- [ ] **Person recognition** - "Who came home?"

### Action Layer
- [x] **Camera control** - Pan/tilt/zoom
- [x] **Browser automation** - UI-agent
- [ ] **Physical actuation** - Servo/robotic arm
- [ ] **Notification** - Alerts on significant events

### Memory Layer
- [x] **Short-term** - Ring buffer (30 min)
- [ ] **Long-term** - Event database (SQLite)
- [x] **Conversation** - JSONL sessions
- [x] **Transcripts** - Voice recordings

### Integration Layer
- [x] **Voice → Action** - Voice typing → Claude Code
- [ ] **Voice → Vision** - "Computer, look at X"
- [ ] **Continuous monitoring** - Background daemon
- [ ] **Multi-camera** - Unified view

---

## Related Sessions

- **5fc36dcc-a09d-40fa-8e32-2baaed85f52e** - Initial vision session (2026-01-08)
- **e2c9ece8-47f3-475b-8bac-52205ced0c3f** - RTSP breakthrough + pan experiment (2026-01-10/11)

## Resume Commands

```bash
claude --resume 5fc36dcc-a09d-40fa-8e32-2baaed85f52e
claude --resume e2c9ece8-47f3-475b-8bac-52205ced0c3f
```
