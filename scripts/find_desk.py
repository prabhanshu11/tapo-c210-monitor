#!/usr/bin/env python3
"""Find desk with laptops/monitors by sweeping camera."""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from tapo_c210_monitor.stream import StreamCapture
from tapo_c210_monitor.ptz_mapper import ONVIFPTZController
from tapo_c210_monitor.vision.llm_vision import LLMVision
from tapo_c210_monitor.health_check import CameraHealthCheck


SWEEP_SEQUENCE = [
    ("top-left", "left", 1.5, "up", 1.0),
    ("top-center", "right", 1.5, None, 0),
    ("top-right", "right", 1.5, None, 0),
    ("mid-right", None, 0, "down", 1.0),
    ("mid-center", "left", 1.5, None, 0),
    ("mid-left", "left", 1.5, None, 0),
    ("bot-left", None, 0, "down", 1.0),
    ("bot-center", "right", 1.5, None, 0),
    ("bot-right", "right", 1.5, None, 0),
]


def find_desk(output_dir: Path, confidence_threshold: float = 0.6):
    output_dir.mkdir(parents=True, exist_ok=True)
    captured_frames = []
    
    print("=" * 60)
    print("TAPO C210 DESK FINDER")
    print(f"Output: {output_dir}")
    print("=" * 60)
    
    host = os.getenv("TAPO_HOST")
    user = os.getenv("TAPO_USERNAME")
    passwd = os.getenv("TAPO_PASSWORD")
    rtsp_url = f"rtsp://{user}:{passwd}@{host}/stream1"
    
    print(f"\n[Init] Connecting to camera at {host}...")
    
    stream = StreamCapture(rtsp_url)
    ptz = ONVIFPTZController()
    vision = LLMVision(model="gemini-3")
    health = CameraHealthCheck()
    
    stream.connect()
    print("[Init] RTSP connected")
    
    ptz.connect()
    print("[Init] ONVIF PTZ connected")
    
    # Check initial tilt for anomalies
    initial_pos = ptz.get_position()
    if initial_pos:
        tilt_anomaly, tilt_msg = health.check_tilt_anomaly(initial_pos.tilt)
        if tilt_anomaly:
            print(f"\n[WARNING] {tilt_msg}")
    
    print("\n[Sweep] Starting camera sweep (9 positions)...")
    print()
    
    best_result = None
    best_position = None
    
    DESK_PROMPT = """Look at this security camera image carefully.

Is there a COMPUTER DESK visible with ANY of these: laptop, monitor screen, keyboard, or computer setup?

IMPORTANT: Reply in this EXACT format:
- If desk IS visible: "DESK_VISIBLE: [confidence 0.0-1.0] - [brief description]"
- If NO desk visible: "NO_DESK: [what you see instead]"

Be strict - only say DESK_VISIBLE if you can clearly see a workspace with computer equipment."""

    for i, (name, pan_dir, pan_dur, tilt_dir, tilt_dur) in enumerate(SWEEP_SEQUENCE):
        print(f"[{i+1}/9] Position: {name}")
        
        if tilt_dir:
            if tilt_dir == "up":
                ptz.tilt_up(duration=tilt_dur)
            else:
                ptz.tilt_down(duration=tilt_dur)
        if pan_dir:
            if pan_dir == "left":
                ptz.pan_left(duration=pan_dur)
            else:
                ptz.pan_right(duration=pan_dur)
        
        time.sleep(1.0)
        
        frame = stream.get_frame()
        if frame is None:
            print("  [Error] Failed to capture frame")
            continue
        
        from PIL import Image
        img = Image.fromarray(frame)
        timestamp = int(time.time())
        saved_path = output_dir / f"{name}_{timestamp}.jpg"
        img.save(saved_path)
        captured_frames.append(saved_path)
        print(f"  [Capture] Saved: {saved_path.name}")
        
        print("  [Vision] Analyzing...")
        try:
            result = vision.analyze_screen(saved_path, task=DESK_PROMPT)
            description = result.screen_description
            print(f"  [Vision] {description[:100]}...")
            
            desc_upper = description.upper()
            if "DESK_VISIBLE" in desc_upper:
                try:
                    conf_str = description.split(":")[1].strip()
                    confidence = float(conf_str.split()[0])
                except:
                    confidence = 0.7
                
                print(f"  [Vision] DESK DETECTED! Confidence: {confidence:.2f}")
                
                if confidence > (best_result[1] if best_result else 0):
                    best_result = (description, confidence, saved_path)
                    best_position = name
                
                if confidence >= confidence_threshold:
                    print(f"\n{'='*60}")
                    print("DESK FOUND!")
                    print(f"{'='*60}")
                    print(f"Position: {name}")
                    print(f"Confidence: {confidence:.2f}")
                    print(f"Description: {description}")
                    print(f"Frame: {saved_path}")
                    
                    stream.disconnect()
                    vision.close()
                    return True
            else:
                print(f"  [Vision] No desk at this position")
                
        except Exception as e:
            print(f"  [Vision] Error: {e}")
        
        print()
    
    # === HEALTH CHECK: Detect mount failure ===
    print("\n[Health] Checking for mount failure...")
    is_stuck, health_msg = health.detect_mount_failure(captured_frames)
    
    if is_stuck:
        print(f"\n{'!'*60}")
        print("PHYSICAL ISSUE DETECTED")
        print(f"{'!'*60}")
        print(health_msg)
        print("\nSee docs/PHYSICAL_INCIDENTS.md for resolution steps.")
        print(f"{'!'*60}")
        
        stream.disconnect()
        vision.close()
        return False
    else:
        print(f"  [Health] {health_msg}")
    
    # Sweep complete
    print("\n" + "=" * 60)
    print("SWEEP COMPLETE")
    print("=" * 60)
    
    if best_result:
        print(f"\nBest match: {best_position}")
        print(f"Confidence: {best_result[1]:.2f}")
        print(f"Description: {best_result[0]}")
        print(f"Frame: {best_result[2]}")
    else:
        print("\nNo desk found in any position.")
    
    stream.disconnect()
    vision.close()
    
    print("\nNote: Camera may need manual adjustment to return to best position.")
    return False


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent.parent / "frames" / f"desk_search_{timestamp}"
    find_desk(output_dir)
