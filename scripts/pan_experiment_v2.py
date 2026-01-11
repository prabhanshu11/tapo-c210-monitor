#!/usr/bin/env python3
"""Pan Experiment v2 - Using Ring Buffer + LLM Vision.

This experiment:
1. Starts the ring buffer (if not running)
2. Captures "before" frames
3. Pans the camera
4. Captures "after" frames
5. Sends both to LLM to detect/describe the change

Usage:
    # Start ring buffer first (in separate terminal):
    cd ringbuffer && source ../.env
    ./ringbuffer -rtsp "rtsp://${TAPO_USERNAME}:${TAPO_PASSWORD}@${TAPO_HOST}/stream1"

    # Run experiment:
    uv run python scripts/pan_experiment_v2.py --direction right --duration 2.0
"""

import os
import sys
import time
import argparse
import httpx
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tapo_c210_monitor.ptz_mapper import ONVIFPTZController
from tapo_c210_monitor.change_detector import LLMVisionAnalyzer, ChangeEvent


def get_frames_from_ringbuffer(
    seconds_ago: list,
    output_dir: str,
    ringbuffer_url: str = "http://localhost:8085"
) -> list:
    """Fetch frames from ring buffer."""
    params = {
        "seconds_ago": ",".join(str(s) for s in seconds_ago),
        "output_dir": output_dir,
    }
    resp = httpx.get(f"{ringbuffer_url}/frames", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("frames", [])


def check_ringbuffer_status(ringbuffer_url: str = "http://localhost:8085") -> dict:
    """Check if ring buffer is running."""
    try:
        resp = httpx.get(f"{ringbuffer_url}/status", timeout=5)
        return resp.json()
    except Exception as e:
        return {"error": str(e), "running": False}


def run_pan_experiment(
    direction: str = "right",
    duration: float = 2.0,
    speed: float = 0.5,
    ringbuffer_url: str = "http://localhost:8085",
    output_dir: str = "/tmp/pan_experiment_v2",
):
    """Run the pan experiment."""

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = os.path.join(output_dir, f"pan_{direction}_{timestamp}")
    os.makedirs(experiment_dir, exist_ok=True)

    print("=" * 60)
    print("PAN EXPERIMENT v2 (Ring Buffer + LLM Vision)")
    print("=" * 60)

    # Check ring buffer
    print("\n[1/6] Checking ring buffer...")
    status = check_ringbuffer_status(ringbuffer_url)
    if not status.get("running"):
        print(f"ERROR: Ring buffer not running at {ringbuffer_url}")
        print(f"Status: {status}")
        print("\nStart it with:")
        print('  cd ringbuffer && source ../.env')
        print('  ./ringbuffer -rtsp "rtsp://${TAPO_USERNAME}:${TAPO_PASSWORD}@${TAPO_HOST}/stream1"')
        return None

    print(f"  Buffer has {status.get('segment_count', 0)} segments")
    print(f"  Buffer duration: {status.get('buffer_seconds', 0):.1f}s")

    # Connect to camera
    print("\n[2/6] Connecting to camera...")
    ctrl = ONVIFPTZController()
    if not ctrl.connect():
        print("ERROR: Failed to connect to camera")
        return None

    pos_before = ctrl.get_position()
    print(f"  Position before: pan={pos_before.pan:.4f}, tilt={pos_before.tilt:.4f}")

    # Capture before frames
    print("\n[3/6] Capturing 'before' frames...")
    # Get frames from 5-10 seconds ago (to ensure segments are complete)
    before_frames = get_frames_from_ringbuffer(
        [5, 8],
        os.path.join(experiment_dir, "before"),
        ringbuffer_url
    ) or []
    print(f"  Captured {len(before_frames)} frames")
    for f in before_frames:
        print(f"    - {os.path.basename(f)}")

    # Pan the camera
    print(f"\n[4/6] Panning {direction.upper()} for {duration}s (speed={speed})...")
    if direction == "left":
        ctrl.pan_left(duration=duration, speed=speed)
    elif direction == "right":
        ctrl.pan_right(duration=duration, speed=speed)
    elif direction == "up":
        ctrl.tilt_up(duration=duration, speed=speed)
    elif direction == "down":
        ctrl.tilt_down(duration=duration, speed=speed)

    # Wait for camera to settle and buffer to update
    print("  Waiting for camera to settle...")
    time.sleep(2)

    pos_after = ctrl.get_position()
    print(f"  Position after: pan={pos_after.pan:.4f}, tilt={pos_after.tilt:.4f}")
    print(f"  Movement: pan delta={pos_after.pan - pos_before.pan:.4f}")

    # Capture after frames
    print("\n[5/6] Capturing 'after' frames...")
    # Get frames from 5-8 seconds ago (after the pan completed)
    after_frames = get_frames_from_ringbuffer(
        [5, 8],
        os.path.join(experiment_dir, "after"),
        ringbuffer_url
    ) or []
    print(f"  Captured {len(after_frames)} frames")
    for f in after_frames:
        print(f"    - {os.path.basename(f)}")

    # Analyze with LLM
    print("\n[6/6] Analyzing with LLM Vision...")
    try:
        analyzer = LLMVisionAnalyzer()

        event = ChangeEvent(
            timestamp=time.time(),
            change_score=0.0,  # Not computed in this experiment
            frames_before=before_frames,
            frames_after=after_frames,
        )

        analysis = analyzer.analyze_change(event)
        event.llm_analysis = analysis

        print("\n" + "=" * 60)
        print("LLM ANALYSIS")
        print("=" * 60)
        print(analysis)

        # Save results
        results = {
            "timestamp": timestamp,
            "direction": direction,
            "duration": duration,
            "speed": speed,
            "position_before": {"pan": pos_before.pan, "tilt": pos_before.tilt},
            "position_after": {"pan": pos_after.pan, "tilt": pos_after.tilt},
            "frames_before": before_frames,
            "frames_after": after_frames,
            "llm_analysis": analysis,
        }

        import json
        results_file = os.path.join(experiment_dir, "results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {results_file}")

        return results

    except ValueError as e:
        print(f"WARNING: LLM analysis skipped: {e}")
        print("Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable")
        return None


def main():
    parser = argparse.ArgumentParser(description="Pan Experiment v2")
    parser.add_argument(
        "--direction",
        choices=["left", "right", "up", "down"],
        default="right",
        help="Pan direction"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=2.0,
        help="Pan duration in seconds"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=0.5,
        help="Pan speed (0.0-1.0)"
    )
    parser.add_argument(
        "--ringbuffer-url",
        default="http://localhost:8085",
        help="Ring buffer API URL"
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/pan_experiment_v2",
        help="Output directory for frames and results"
    )
    args = parser.parse_args()

    run_pan_experiment(
        direction=args.direction,
        duration=args.duration,
        speed=args.speed,
        ringbuffer_url=args.ringbuffer_url,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
