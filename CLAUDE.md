# Claude Code Project Instructions

## IMPORTANT: Read These First
1. **Parent context**: `~/Programs/CLAUDE.md` - Cross-project principles (uv, VPS rules, etc.)
2. **Agent behavior**: `./agents.md` - How to work in this project
3. **Current state**: `./progress_actual.md` - Decisions, constraints, next steps

## Project Overview
Intelligent LLM-powered monitoring system for TP-Link TAPO C210 camera with Android automation capabilities.

## Android Screenshot Guidelines

### Known Issue: API Image Size Limits
When using Claude Code with many images in a conversation, there's a strict limit:
- **Maximum dimension: 2000 pixels** (for many-image requests)
- Android devices often have tall screens (e.g., 1080x2400) that exceed this limit
- Once a conversation accumulates too many oversized images, the API rejects ALL requests

**Symptoms:**
```
API Error: 400 ... "At least one of the image dimensions exceed max allowed size for many-image requests: 2000 pixels"
```

### Recommended Screenshot Dimensions
For Android automation with Claude Code, resize screenshots before reading:

| Device Aspect | Original | Recommended | Command |
|--------------|----------|-------------|---------|
| 9:20 (tall)  | 1080x2400 | 855x1900 | `convert - -resize 'x1900>'` |
| 9:19 | 1080x2280 | 900x1900 | `convert - -resize 'x1900>'` |
| 9:16 | 1080x1920 | 1080x1920 | No resize needed |

### Screenshot Capture with Auto-Resize
```bash
# Capture and resize in one command (requires ImageMagick)
adb exec-out screencap -p | convert - -resize 'x1900>' /tmp/screen.png

# Or save original then resize
adb exec-out screencap -p > /tmp/screen_raw.png
convert /tmp/screen_raw.png -resize 'x1900>' /tmp/screen.png
```

### Best Practices for Image-Heavy Sessions
1. **Resize before reading**: Always resize screenshots to under 2000px
2. **Use UI Automator XML**: Prefer `uiautomator dump` for element locations instead of visual analysis
3. **Start fresh sessions**: For long automation tasks, consider starting new conversations periodically
4. **Delete old screenshots**: Clean up screenshot files between automation runs

### If a Conversation Gets Stuck
The conversation JSONL file can be fixed by stripping base64 image data:
```python
import re
import shutil

src = '~/.claude/projects/.../SESSION_ID.jsonl'
shutil.copy(src, src + '.backup')

with open(src, 'r') as f:
    content = f.read()

cleaned = re.sub(r'"data":"[A-Za-z0-9+/=]{100,}"',
                 '"data":"[IMAGE_REMOVED]"', content)

with open(src, 'w') as f:
    f.write(cleaned)
```

## Android Automation Architecture

### Preferred Approach: Hybrid UI Detection
1. **Primary**: Use `uiautomator dump` to get element bounds (fast, accurate)
2. **Fallback**: Use LLM vision via OpenRouter for complex UI analysis
3. **Avoid**: Reading raw screenshots into Claude Code context repeatedly

### Existing Modules
- `src/tapo_c210_monitor/android/controller.py` - ADB wrapper
- `src/tapo_c210_monitor/android/intelligent_screen.py` - LLM-based UI detection
- `src/tapo_c210_monitor/vision/llm_vision.py` - OpenRouter vision API

## Environment Variables
```
OPENROUTER_API_KEY=sk-or-...  # For LLM vision analysis
TAPO_HOST=...                  # Camera IP
TAPO_USERNAME=...              # Camera account
TAPO_PASSWORD=...              # Camera password
```
