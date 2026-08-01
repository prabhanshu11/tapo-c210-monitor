# Physical Incidents Log

## Camera Mount Failures

### Incident 2026-01-15 23:29 - Tape Mount Failure

**Summary**: Camera fell from wall-mounted position due to tape losing adhesive grip.

**Details**:
- **Time**: 2026-01-15 23:29 (unix: 1768500000)
- **Cause**: Adhesive tape securing camera to wall lost grip
- **Result**: Camera fell and became stuck on/against the door
- **Impact**:
  - PTZ commands no longer move camera view meaningfully
  - All sweep positions show similar images (stuck view)
  - Autonomous desk-finding task blocked

**Symptoms Observed** (for future detection):
1. PTZ position feedback shows movement (pan/tilt values change)
2. BUT captured frames show no meaningful change in view
3. LLM analysis shows same/similar scene across all positions
4. Camera may report impossible/extreme tilt values

**Detection Logic** (to implement):
```python
def detect_mount_failure(frames: list[Path]) -> bool:
    """
    Detect if camera is physically stuck/fallen.

    Signs:
    1. All frames very similar (image hash comparison)
    2. PTZ reports movement but view unchanged
    3. Extreme tilt angles (>80 degrees)
    """
    # Compare image hashes across positions
    # If >70% similarity across all frames, likely stuck
    pass
```

**Resolution**:
1. User must physically remount camera
2. Consider more permanent mounting solution (screws, dedicated bracket)
3. Test PTZ range after remount

A basic algorithm was developed and is now part of the code to detect this issue. Needs to develop more test, and an endpoint on an UI.

**User Note**:
> "the camera had physically been stuck at a position because of it losing the grip from the tape that it was stuck to to the wall. So it was stuck and it fell down on the door."

---

## Prevention Recommendations

1. **Mount Type**: Use screw-mounted bracket instead of adhesive tape
2. **Weight Distribution**: Ensure mount can handle PTZ motor torque
3. **Temperature**: Adhesive weakens in heat - consider ambient conditions
4. **Vibration**: PTZ movements may gradually loosen tape over time

## Future Detection Features

- [ ] Image similarity check across sweep positions
- [ ] Alert when all positions show same scene
- [ ] Tilt angle anomaly detection
- [ ] Periodic "camera health check" that verifies PTZ actually changes view
