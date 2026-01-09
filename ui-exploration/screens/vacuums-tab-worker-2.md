# Vacuums Tab Screen - Worker 2 Documentation

**Documented by:** Worker-2 (emulator-5556)
**Timestamp:** 2026-01-09T06:58:00Z
**Package:** com.tplink.iot

## Screen Overview
The Vacuums tab in the Tapo app. Shows robot vacuum devices or an empty state prompting to add one.

## UI Structure (Empty State)

### Header (bounds: [0,0][320,72])

| Element | Resource ID | Type | Content-Desc | Bounds | Clickable |
|---------|-------------|------|--------------|--------|-----------|
| Add Vacuum | `iv_add` | ImageView | "Add Robot Vacuum" | [272,24][320,72] | Yes |

### Empty State Content (bounds: [0,72][320,590])

| Element | Resource ID | Type | Text | Bounds |
|---------|-------------|------|------|--------|
| Empty Image | `iv_empty` | ImageView | - | [40,219][280,365] |
| Title | `tv_title` | TextView | "Welcome to Robot Vacuums" | [0,385][320,408] |
| Description | `tv_tip` | TextView | "Add a robot vacuum and clean whenever, wherever..." | - |

### Key Resource IDs
- `bg_status` - Background status view
- `view_header` - Header container
- `layout_refresh` - Pull-to-refresh container
- `layout_empty` - Empty state container

## Navigation Paths

### From this screen:
- **Tap Add Vacuum** -> `add-vacuum` (vacuum setup flow)
- **Pull down** -> Refresh vacuum list

## Discovered Screens
- `add-vacuum` - Tap add button [272,24][320,72]

## Quick Reference - Tap Coordinates

| Action | Tap Point | Description |
|--------|-----------|-------------|
| Add Vacuum | tap(296, 48) | Start vacuum setup |
| Home Tab | tap(32, 615) | Switch to home |

## Notes
- Screen shows empty state when no vacuums configured
- Pull-to-refresh available via layout_refresh
- No camera access needed - stable screen
