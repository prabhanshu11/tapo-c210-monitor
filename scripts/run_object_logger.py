#!/usr/bin/env python3
"""CLI for continuous object detection and querying the detection database.

Usage:
    # Run scanner (periodic YOLO + optional LLM)
    uv run python scripts/run_object_logger.py

    # YOLO-only, 60s interval
    uv run python scripts/run_object_logger.py --interval 60 --no-llm

    # Query: what objects in last hour?
    uv run python scripts/run_object_logger.py --query "person" --last-hours 1

    # Query: class summary
    uv run python scripts/run_object_logger.py --summary --last-hours 24
"""

import argparse
import time
import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tapo_c210_monitor.detection import YOLODetector, ObjectLogger, SceneScanner


def run_scanner(args):
    """Start continuous scanning."""
    detector = YOLODetector(
        confidence_threshold=args.threshold,
    )
    print(f"YOLO loaded on {detector.device}")

    db_path = Path(__file__).resolve().parent.parent / "data" / "object_detections.db"
    logger = ObjectLogger(db_path)

    llm_analyzer = None
    if not args.no_llm:
        try:
            from tapo_c210_monitor.change_detector import LLMVisionAnalyzer
            llm_analyzer = LLMVisionAnalyzer()
            print(f"LLM analyzer: {llm_analyzer.model}")
        except (ValueError, ImportError) as e:
            print(f"LLM disabled: {e}")

    scanner = SceneScanner(
        ringbuffer_url=args.ringbuffer_url,
        detector=detector,
        logger=logger,
        llm_analyzer=llm_analyzer,
        periodic_interval=args.interval,
        llm_interval=args.llm_interval,
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

    if args.summary:
        print(f"\n=== Object Detection Summary (last {args.last_hours}h) ===\n")
        rows = logger.get_class_summary(hours=args.last_hours)
        if not rows:
            print("No detections found.")
        else:
            print(f"{'Class':<20} {'Count':>6} {'Avg Conf':>9} {'First Seen':>20} {'Last Seen':>20}")
            print("-" * 77)
            for r in rows:
                first = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["first_seen"]))
                last = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["last_seen"]))
                print(f"{r['class_name']:<20} {r['detection_count']:>6} "
                      f"{r['avg_confidence']:>9.3f} {first:>20} {last:>20}")

    elif args.query:
        # Try FTS first, fall back to class name timeline
        print(f"\n=== Search: '{args.query}' (last {args.last_hours}h) ===\n")

        # Timeline for specific object class
        rows = logger.get_object_timeline(args.query, hours=args.last_hours)
        if rows:
            print(f"Found {len(rows)} detections of '{args.query}':\n")
            for r in rows:
                ts = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(r["frame_timestamp_unix"]))
                print(f"  {ts}  conf={r['confidence']:.2f}  "
                      f"type={r['scan_type']}  cam={r['source_camera']}")
        else:
            # Try FTS search
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
        # Show recent scans
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

    # Query mode
    parser.add_argument("--query", type=str,
                        help="Search mode: query by object class or FTS")
    parser.add_argument("--summary", action="store_true",
                        help="Show class summary for time window")
    parser.add_argument("--last-hours", type=int, default=24,
                        help="Time window for queries (default: 24)")

    args = parser.parse_args()

    if args.query or args.summary:
        query_database(args)
    else:
        run_scanner(args)


if __name__ == "__main__":
    main()
