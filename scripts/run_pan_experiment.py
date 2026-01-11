#!/usr/bin/env python3
"""Run the Pan Control Experiment.

Usage:
    # Quick test (pan left once)
    uv run python scripts/run_pan_experiment.py

    # Full test (all directions)
    uv run python scripts/run_pan_experiment.py --full

    # Specific direction
    uv run python scripts/run_pan_experiment.py --direction right --duration 2.0
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tapo_c210_monitor.experiments.pan_control import (
    PanControlExperiment,
    PanDirection,
)


def main():
    parser = argparse.ArgumentParser(description="Pan Control Experiment")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full test (all 4 directions)",
    )
    parser.add_argument(
        "--direction",
        choices=["left", "right", "up", "down"],
        default="left",
        help="Pan direction (default: left)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=1.0,
        help="Pan duration in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/tmp/pan_experiment",
        help="Output directory for frames",
    )
    parser.add_argument(
        "--subnet",
        type=str,
        default="192.168.29",
        help="Network subnet for camera discovery",
    )
    parser.add_argument(
        "--camera-ip",
        type=str,
        default=None,
        help="Skip discovery and use this camera IP directly",
    )

    args = parser.parse_args()

    # Map string to enum
    direction_map = {
        "left": PanDirection.LEFT,
        "right": PanDirection.RIGHT,
        "up": PanDirection.UP,
        "down": PanDirection.DOWN,
    }

    exp = PanControlExperiment(
        output_dir=args.output,
        subnet=args.subnet,
        camera_ip=args.camera_ip,
    )

    print("=" * 60)
    print("PAN CONTROL EXPERIMENT")
    print("=" * 60)
    print()

    if not exp.setup():
        print("\nExperiment setup failed!")
        print("\nChecklist:")
        print("  [ ] Camera is powered on")
        print("  [ ] Camera is connected to WiFi")
        print("  [ ] Android emulator is running (tapo_playstore)")
        print("  [ ] Tapo app is open on camera live view")
        sys.exit(1)

    print()

    if args.full:
        print("Running full test sequence (all 4 directions)...")
        results = exp.run_full_test()

        print("\n" + "=" * 60)
        print("RESULTS SUMMARY")
        print("=" * 60)
        for r in results:
            status = "DETECTED" if r.visual_shift_detected else "NOT DETECTED"
            print(f"  {r.direction:6s}: {status} (magnitude: {r.shift_magnitude:.3f})")

        print(f"\nFrames saved to: {args.output}/frames/")
    else:
        direction = direction_map[args.direction]
        result = exp.run(direction, pan_duration=args.duration)

        print("\n" + "=" * 60)
        print("RESULT")
        print("=" * 60)
        status = "DETECTED" if result.visual_shift_detected else "NOT DETECTED"
        print(f"  Direction: {result.direction}")
        print(f"  Shift: {status}")
        print(f"  Magnitude: {result.shift_magnitude:.3f}")
        print(f"\n  Baseline: {result.baseline_frame}")
        print(f"  Post-PAN: {result.post_pan_frame}")

    print("\nOpen the frame images to visually verify camera movement!")


if __name__ == "__main__":
    main()
