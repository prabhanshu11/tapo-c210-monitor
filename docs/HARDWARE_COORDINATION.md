# Hardware Coordination: Object Detection ↔ ESP32/Pi Zero

## Object Detection Work (This Project)
- Runs entirely on desktop (camera → RTSP → YOLO → SQLite)
- Does NOT touch ESP32 serial, BLE, or any GPIO
- Does NOT modify Pi Zero firmware or keyboard API
- No conflicts with BLE mouse passthrough or BT keyboard work

## Future: Actuator Integration (Gas Knob Experiment)
When ready to add physical actuator control:

### What We Need from ESP32
1. **Servo control command** added to serial protocol:
   - `SERVO:angle` — set servo to 0-180 degrees
   - `SERVO:STATUS` — report current angle
2. **GPIO pin**: One PWM-capable pin (suggest GPIO 13 or 14)
3. **No changes to existing**: MOUSE/CLICK/SCROLL commands must keep working
4. **Firmware change**: Add `#include <ESP32Servo.h>` alongside existing BLE libs

### What We Need from Pi Zero 2W
- Nothing for now (keyboard work is independent)
- Future possibility: Edge detection if always-on monitoring needed

### Pin Allocation (ESP32)
| Pin | Current Use | Proposed Addition |
|-----|------------|-------------------|
| TX/RX | Serial (115200 baud) | No change |
| BLE | Mouse HID | No change |
| GPIO 13 | Free | Servo PWM for actuator |
| GPIO 14 | Free | Reserve for 2nd servo |

### Serial Protocol Extension
```
Existing:
  MOUSE:dx,dy   → Move mouse
  CLICK:left     → Click
  SCROLL:n       → Scroll
  STATUS         → Report BLE status

Proposed addition:
  SERVO:angle    → Set servo (0-180)
  SERVO:STATUS   → Report servo angle
```

### Integration Timeline
1. Object detection + logging (current work — desktop only)
2. Servo wiring + firmware update (needs ESP32 agent)
3. Camera → detect object → command servo → verify via camera
