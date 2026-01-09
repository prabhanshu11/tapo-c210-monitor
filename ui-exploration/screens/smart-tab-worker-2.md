# Smart Tab Screen - Worker 2 Documentation

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T06:54:00Z
**Package:** com.tplink.iot

## Screen Overview
The Smart/Automation tab in the Tapo app. Shows shortcuts and automation templates for controlling devices with one tap or automated triggers.

## UI Structure

### Header (bounds: [0,24][320,72])

| Element | Resource ID | Type | Content-Desc | Bounds | Clickable |
|---------|-------------|------|--------------|--------|-----------|
| History | `smart_history_action` | Button | "History" | [224,24][272,72] | Yes |
| Add Smart Action | `smart_add_action` | Button | "Add Smart Action" | [272,24][320,72] | Yes |

### Tab Layout (bounds: [6,72][320,124])

| Tab | Text | Content-Desc | Bounds | Selected |
|-----|------|--------------|--------|----------|
| Recommended | "Recommended" | "Recommended" | [6,72][153,124] | Yes |
| Shortcuts | "Shortcuts" | "Shortcuts" | [153,72][255,124] | No |
| Automation | "Automation" | "Automation" | [255,72][320,124] | No |

### Recommended View Content (bounds: [0,128][320,590])

#### Shortcut Section (bounds: [0,157][320,447])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Section Header | `tv_text1` | TextView | "Shortcut" | "Recommended Shortcuts" | [20,128][300,147] | No |
| Leave Home Card | `cv_root` | Button | "Leave Home" | "Leave Home, Turn off all your Tapo devices with one simple tap." | [16,157][181,423] | Yes |
| Arrive Home Card | `cv_root` | Button | "Arrive Home" | "Arrive Home, Turn on all your Tapo devices with one simple tap." | [193,157][320,423] | Yes |

#### Automation Section (bounds: [0,447][320,590])

| Element | Resource ID | Type | Text | Content-Desc | Bounds | Clickable |
|---------|-------------|------|------|--------------|--------|-----------|
| Section Header | `tv_text2` | TextView | "Automation" | "Recommended Automation" | [20,447][300,466] | No |
| Tap to Alarm | `layout_automation_item` | Button | "Tap to Alarm" | "Recommended Automation, Tap to Alarm, 0 devices available" | [16,476][304,590] | Yes |

### Bottom Navigation (bounds: [0,590][320,640])
Same structure as other tabs. "Smart" tab is selected.

## Navigation Paths

### From this screen:
- **Tap History** -> `smart-history` (execution log)
- **Tap Add Smart Action** -> `add-smart-action` (create new shortcut/automation)
- **Tap Shortcuts Tab** -> View all shortcuts
- **Tap Automation Tab** -> View all automations
- **Tap Leave Home Card** -> `shortcut-leave-home` (configure leave home shortcut)
- **Tap Arrive Home Card** -> `shortcut-arrive-home` (configure arrive home shortcut)
- **Tap Tap to Alarm** -> `automation-tap-alarm` (configure alarm automation)

## Discovered Screens
- `smart-history` - Tap history button [224,24][272,72]
- `add-smart-action` - Tap add button [272,24][320,72]
- `shortcut-leave-home` - Tap Leave Home card [16,157][181,423]
- `shortcut-arrive-home` - Tap Arrive Home card [193,157][320,423]
- `automation-tap-alarm` - Tap Tap to Alarm [16,476][304,590]

## Key Resource IDs
- `smart_header` - Header container
- `smart_tab` - Tab layout (HorizontalScrollView)
- `smart_view_pager` - Content ViewPager
- `rv_shortcut` - Shortcuts RecyclerView
- `rv_automation` - Automation RecyclerView
- `refresh_layout` - Pull-to-refresh container
- `nested_scroll_view` - Scrollable content

## Shortcut Card Structure
Each shortcut card contains:
- `iv_shortcut` - Illustration image
- `ll_shortcut` - Text container
- `tv_title` - Shortcut name
- `tv_subtitle` - Shortcut description

## Notes
- Screen shows recommended templates on first load
- No camera access needed - stable screen
- Shortcuts allow one-tap actions
- Automations allow trigger-based actions
- "0 devices available" indicates no compatible devices for that automation
