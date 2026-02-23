#!/usr/bin/env python3
"""CLI for continuous object detection and querying the detection database.

Usage:
    # Run scanner (periodic YOLO + optional LLM) — passive, no camera movement
    uv run python scripts/run_object_logger.py
    uv run python scripts/run_object_logger.py --interval 60 --no-llm

    # Full autonomous mode with PTZ camera movement
    uv run python scripts/run_object_logger.py --ptz --sweep-interval 300

    # Query: what objects in last hour?
    uv run python scripts/run_object_logger.py --query "person" --last-hours 1

    # Query: class summary
    uv run python scripts/run_object_logger.py --summary --last-hours 24

    # Query: active object tracks
    uv run python scripts/run_object_logger.py --tracks

    # Query: unresolved edge cases
    uv run python scripts/run_object_logger.py --edge-cases

    # Generate daily summary report
    uv run python scripts/run_object_logger.py --generate-summary
"""

import argparse
import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tapo_c210_monitor.detection import (
    YOLODetector, ObjectLogger, ActiveSceneManager, FrameStore,
)


def run_scanner(args):
    """Start continuous scanning."""
    detector = YOLODetector(confidence_threshold=args.threshold)
    print(f"YOLO loaded on {detector.device}")

    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "object_detections.db"
    logger = ObjectLogger(db_path)

    llm_analyzer = None
    if not args.no_llm:
        try:
            from tapo_c210_monitor.change_detector import LLMVisionAnalyzer
            llm_analyzer = LLMVisionAnalyzer()
            print(f"LLM analyzer: {llm_analyzer.model}")
        except (ValueError, ImportError) as e:
            print(f"LLM disabled: {e}")

    ptz = None
    if args.ptz:
        from dotenv import load_dotenv
        load_dotenv(project_root / ".env")

        host = os.getenv("TAPO_HOST")
        user = os.getenv("TAPO_USERNAME")
        passwd = os.getenv("TAPO_PASSWORD")
        if not all([host, user, passwd]):
            print("Error: --ptz requires TAPO_HOST, TAPO_USERNAME, TAPO_PASSWORD in .env")
            sys.exit(1)

        from tapo_c210_monitor.onvif_ptz import TapoPTZ
        ptz = TapoPTZ(host, user, passwd)
        if not ptz.connect():
            print("Error: Failed to connect PTZ")
            sys.exit(1)
        print(f"PTZ connected to {host}")

    frame_store = FrameStore(base_dir=project_root / "data" / "frames")

    scanner = ActiveSceneManager(
        ringbuffer_url=args.ringbuffer_url,
        detector=detector,
        logger=logger,
        ptz=ptz,
        llm_analyzer=llm_analyzer,
        frame_store=frame_store,
        scan_interval=args.interval,
        sweep_interval=args.sweep_interval,
        settle_time=args.settle_time,
        home_position=(args.home_pan, args.home_tilt),
    )

    try:
        scanner.start()
    except KeyboardInterrupt:
        print("\nStopping scanner...")
        scanner.stop()
        logger.close()


def query_database(args):
    """Query the detection database."""
    db_path = Path(__file__).resolve().parent.parent / "data" / "object_detections.db"

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        print("Run the scanner first to create it.")
        sys.exit(1)

    logger = ObjectLogger(db_path)

    if args.tracks:
        print(f"\n=== Active Object Tracks ===\n")
        rows = logger.get_active_tracks()
        if not rows:
            print("No active tracks.")
        else:
            print(f"{'Class':<15} {'Duration':>10} {'Detections':>11} "
                  f"{'Avg Conf':>9} {'Pan':>6} {'Tilt':>6}")
            print("-" * 63)
            for r in rows:
                dur = r["duration_seconds"]
                dur_str = f"{dur // 60}m{dur % 60:02d}s" if dur >= 60 else f"{dur}s"
                pan_str = f"{r['camera_pan']:.1f}" if r["camera_pan"] is not None else "n/a"
                tilt_str = f"{r['camera_tilt']:.1f}" if r["camera_tilt"] is not None else "n/a"
                print(f"{r['class_name']:<15} {dur_str:>10} {r['total_detections']:>11} "
                      f"{r['avg_confidence']:>9.3f} {pan_str:>6} {tilt_str:>6}")

    elif args.edge_cases:
        print(f"\n=== Unresolved Edge Cases (last {args.last_hours}h) ===\n")
        rows = logger.get_edge_cases(hours=args.last_hours)
        if not rows:
            print("No unresolved edge cases.")
        else:
            for r in rows:
                ts_unix = r.get("frame_timestamp_unix")
                ts_str = time.strftime("%H:%M:%S", time.localtime(ts_unix)) if ts_unix else "?"
                cls = r.get("class_name") or "unknown"
                conf = r.get("confidence")
                conf_str = f" conf={conf:.2f}" if conf else ""
                print(f"  [{ts_str}] {r['case_type']}: {cls}{conf_str} — {r.get('description', '')}")

    elif args.generate_summary:
        _generate_summary(logger, args)

    elif args.summary:
        print(f"\n=== Object Detection Summary (last {args.last_hours}h) ===\n")
        rows = logger.get_class_summary(hours=args.last_hours)
        if not rows:
            print("No detections found.")
        else:
            print(f"{'Class':<20} {'Count':>6} {'Avg Conf':>9} "
                  f"{'First Seen':>20} {'Last Seen':>20}")
            print("-" * 77)
            for r in rows:
                first = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["first_seen"]))
                last = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["last_seen"]))
                print(f"{r['class_name']:<20} {r['detection_count']:>6} "
                      f"{r['avg_confidence']:>9.3f} {first:>20} {last:>20}")

    elif args.query:
        print(f"\n=== Search: '{args.query}' (last {args.last_hours}h) ===\n")
        rows = logger.get_object_timeline(args.query, hours=args.last_hours)
        if rows:
            print(f"Found {len(rows)} detections of '{args.query}':\n")
            for r in rows:
                ts = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(r["frame_timestamp_unix"]))
                print(f"  {ts}  conf={r['confidence']:.2f}  "
                      f"type={r['scan_type']}  cam={r['source_camera']}")
        else:
            fts_rows = logger.search(args.query)
            if fts_rows:
                print(f"Found {len(fts_rows)} scans matching '{args.query}':\n")
                for r in fts_rows:
                    ts = time.strftime("%Y-%m-%d %H:%M:%S",
                                       time.localtime(r["frame_timestamp_unix"]))
                    summary = (r.get("llm_summary") or "")[:80]
                    print(f"  {ts}  objects={r['objects_count']}  {summary}")
            else:
                print(f"No results for '{args.query}'.")

    else:
        print(f"\n=== Recent Scans ===\n")
        rows = logger.get_recent_scans(limit=10)
        if not rows:
            print("No scans recorded yet.")
        else:
            for r in rows:
                ts = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(r["frame_timestamp_unix"]))
                objects = r.get("object_list") or "(none)"
                print(f"  [{r['scan_type']:<16}] {ts}  {objects}")

    logger.close()


def _generate_summary(logger, args):
    """Generate a daily summary (inline, no separate script dependency)."""
    hours = args.last_hours
    print(f"\n=== Generating Summary (last {hours}h) ===\n")

    data = {
        "class_summary": logger.get_class_summary(hours=hours),
        "tracks": logger.get_tracks_summary(hours=hours),
        "edge_cases": logger.get_edge_cases(hours=hours, unresolved_only=False),
        "scan_stats": logger.get_scan_stats(hours=hours),
        "llm_summaries": logger.get_recent_llm_summaries(hours=hours),
    }

    # Print summary to stdout
    print(f"Scans: {sum(data['scan_stats'].values())} total")
    for st, count in data["scan_stats"].items():
        print(f"  {st}: {count}")

    print(f"\nObject classes: {len(data['class_summary'])}")
    for r in data["class_summary"]:
        print(f"  {r['class_name']}: {r['detection_count']}x (avg conf {r['avg_confidence']:.2f})")

    print(f"\nTracks: {len(data['tracks'])}")
    for r in data["tracks"]:
        dur = r["duration_seconds"]
        dur_str = f"{dur // 60}m" if dur >= 60 else f"{dur}s"
        status = r["track_status"]
        first = time.strftime("%H:%M", time.localtime(r["first_seen_unix"]))
        last = time.strftime("%H:%M", time.localtime(r["last_seen_unix"]))
        print(f"  {r['class_name']} [{status}] {first}–{last} ({dur_str}, {r['total_detections']}x)")

    print(f"\nEdge cases: {len(data['edge_cases'])}")
    for r in data["edge_cases"]:
        print(f"  {r['case_type']}: {r.get('class_name', '?')} — {r.get('description', '')}")

    print(f"\nLLM summaries: {len(data['llm_summaries'])}")

    print("\nUse scripts/daily_summary.py for full LLM-analyzed report.")


def main():
    parser = argparse.ArgumentParser(
        description="Continuous Object Detection & Logging via TAPO Camera"
    )

    # Scanner mode
    parser.add_argument("--interval", type=float, default=30.0,
                        help="Periodic scan interval in seconds (default: 30)")
    parser.add_argument("--no-llm", action="store_true",
                        help="Disable LLM enrichment (YOLO only)")
    parser.add_argument("--llm-interval", type=float, default=300.0,
                        help="Seconds between LLM calls (default: 300)")
    parser.add_argument("--threshold", type=float, default=0.25,
                        help="YOLO confidence threshold (default: 0.25)")
    parser.add_argument("--ringbuffer-url", default="http://localhost:8085",
                        help="Ring buffer HTTP URL")

    # PTZ mode
    parser.add_argument("--ptz", action="store_true",
                        help="Enable PTZ autonomous movement")
    parser.add_argument("--no-ptz", action="store_true", default=True,
                        help="Disable PTZ (default)")
    parser.add_argument("--sweep-interval", type=float, default=300.0,
                        help="Seconds between coverage sweeps (default: 300)")
    parser.add_argument("--settle-time", type=float, default=3.0,
                        help="Seconds to wait after camera move (default: 3)")
    parser.add_argument("--home-pan", type=float, default=0.0,
                        help="Home position pan (default: 0.0)")
    parser.add_argument("--home-tilt", type=float, default=0.0,
                        help="Home position tilt (default: 0.0)")

    # Query mode
    parser.add_argument("--query", type=str,
                        help="Search mode: query by object class or FTS")
    parser.add_argument("--summary", action="store_true",
                        help="Show class summary for time window")
    parser.add_argument("--last-hours", type=int, default=24,
                        help="Time window for queries (default: 24)")
    parser.add_argument("--tracks", action="store_true",
                        help="Show active object tracks")
    parser.add_argument("--edge-cases", action="store_true",
                        help="Show unresolved edge cases")
    parser.add_argument("--generate-summary", action="store_true",
                        help="Generate summary report for time window")

    args = parser.parse_args()

    is_query = args.query or args.summary or args.tracks or args.edge_cases or args.generate_summary
    if is_query:
        query_database(args)
    else:
        run_scanner(args)


if __name__ == "__main__":
    main()
