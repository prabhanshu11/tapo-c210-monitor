#!/usr/bin/env python3
"""Generate a daily summary of camera monitoring data.

Queries 24h of accumulated detection data from SQLite, structures it
into a prompt, sends to LLM via OpenRouter, and writes the result to
data/summaries/YYYY-MM-DD.md.

Usage:
    uv run python scripts/daily_summary.py                # today's summary
    uv run python scripts/daily_summary.py --date 2026-02-22
    uv run python scripts/daily_summary.py --dry-run      # print prompt only
"""

import argparse
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from tapo_c210_monitor.detection import ObjectLogger


def collect_data(logger: ObjectLogger, hours: int = 24) -> dict:
    """Collect all monitoring data for the summary."""
    return {
        "class_summary": logger.get_class_summary(hours=hours),
        "tracks": logger.get_tracks_summary(hours=hours),
        "edge_cases": logger.get_edge_cases(hours=hours, unresolved_only=False),
        "coverage_gaps": logger.get_coverage_gaps(hours=hours),
        "scan_stats": logger.get_scan_stats(hours=hours),
        "llm_summaries": logger.get_recent_llm_summaries(hours=hours),
    }


def build_prompt(data: dict) -> str:
    """Build the LLM analysis prompt from collected data."""
    lines = [
        "You are analyzing 24 hours of camera monitoring data from a Tapo C210 security camera.",
        "",
        "## Detected Objects",
    ]

    if data["class_summary"]:
        lines.append(f"{'Class':<15} {'Count':>6} {'Avg Conf':>9} {'First Seen':>20} {'Last Seen':>20}")
        lines.append("-" * 72)
        for r in data["class_summary"]:
            first = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["first_seen"]))
            last = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["last_seen"]))
            lines.append(f"{r['class_name']:<15} {r['detection_count']:>6} "
                         f"{r['avg_confidence']:>9.2f} {first:>20} {last:>20}")
    else:
        lines.append("No objects detected.")

    lines.extend(["", "## Object Tracks (movement patterns)"])
    if data["tracks"]:
        for r in data["tracks"]:
            dur = r["duration_seconds"]
            dur_str = f"{dur // 60}m" if dur >= 60 else f"{dur}s"
            first = time.strftime("%H:%M", time.localtime(r["first_seen_unix"]))
            last = time.strftime("%H:%M", time.localtime(r["last_seen_unix"]))
            status = r["track_status"]
            departed = ""
            if r.get("departed_at_unix"):
                departed = f", departed at {time.strftime('%H:%M', time.localtime(r['departed_at_unix']))}"
            lines.append(f"- {r['class_name']} [{status}]: entered at {first}, "
                         f"present for {dur_str}, last seen {last}"
                         f" ({r['total_detections']} detections, avg conf {r['avg_confidence']:.2f})"
                         f"{departed}")
    else:
        lines.append("No tracks recorded.")

    lines.extend(["", "## Edge Cases (detection quality issues)"])
    if data["edge_cases"]:
        for r in data["edge_cases"]:
            cls = r.get("class_name") or "unknown"
            conf = f" (conf={r['confidence']:.2f})" if r.get("confidence") else ""
            desc = r.get("description") or ""
            resolved = " [resolved]" if r.get("resolved") else ""
            lines.append(f"- {r['case_type']}: {cls}{conf} — {desc}{resolved}")
    else:
        lines.append("None flagged.")

    lines.extend(["", "## Scan Statistics"])
    total = sum(data["scan_stats"].values())
    lines.append(f"Total scans: {total}")
    for st, count in data["scan_stats"].items():
        lines.append(f"- {st}: {count}")

    lines.extend(["", "## LLM Vision Summaries"])
    if data["llm_summaries"]:
        for r in data["llm_summaries"]:
            ts = time.strftime("%H:%M", time.localtime(r["frame_timestamp_unix"]))
            summary = (r["llm_summary"] or "")[:200]
            lines.append(f"- [{ts}] {summary}")
    else:
        lines.append("No LLM analyses were performed.")

    lines.extend([
        "",
        "## Your Analysis:",
        "1. **Activity Timeline** — What happened throughout the day? Summarize movement patterns.",
        "2. **Anomalies** — Anything unusual or concerning?",
        "3. **Detection Quality** — False positives? Missed objects? Threshold suggestions?",
        "4. **Coverage** — Are there blind spots? Better sweep positions?",
        "5. **Decisions Needed** (checkbox format for human):",
        "   - [ ] List any decisions or actions needed",
    ])

    return "\n".join(lines)


def call_llm(prompt: str, model: str = "google/gemini-3-flash-preview") -> str:
    """Send prompt to OpenRouter and return the response."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    resp = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a security camera monitoring analyst. "
                 "Produce concise, actionable daily reports in markdown format."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 2000,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def write_summary(content: str, date_str: str, model: str, total_scans: int):
    """Write the summary to data/summaries/YYYY-MM-DD.md."""
    project_root = Path(__file__).resolve().parent.parent
    summaries_dir = project_root / "data" / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    output_path = summaries_dir / f"{date_str}.md"
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    header = (
        f"# Camera Monitoring Summary — {date_str}\n\n"
        f"Generated: {now}\n"
        f"Model: {model}\n"
        f"Scans analyzed: {total_scans}\n\n"
        f"---\n\n"
    )

    output_path.write_text(header + content)
    print(f"Summary written to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate daily camera monitoring summary")
    parser.add_argument("--date", type=str, default=None,
                        help="Date to summarize (YYYY-MM-DD, default: today)")
    parser.add_argument("--hours", type=int, default=24,
                        help="Hours of data to analyze (default: 24)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print prompt without calling LLM")
    parser.add_argument("--model", default="google/gemini-3-flash-preview",
                        help="OpenRouter model ID")
    args = parser.parse_args()

    date_str = args.date or time.strftime("%Y-%m-%d")
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "object_detections.db"

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    logger = ObjectLogger(db_path)
    data = collect_data(logger, hours=args.hours)
    prompt = build_prompt(data)

    total_scans = sum(data["scan_stats"].values())
    print(f"Data collected: {total_scans} scans, "
          f"{len(data['class_summary'])} classes, "
          f"{len(data['tracks'])} tracks, "
          f"{len(data['edge_cases'])} edge cases")

    if args.dry_run:
        print("\n=== DRY RUN — LLM Prompt ===\n")
        print(prompt)
        logger.close()
        return

    print(f"Calling {args.model}...")
    analysis = call_llm(prompt, model=args.model)

    output = write_summary(analysis, date_str, args.model, total_scans)
    logger.close()


if __name__ == "__main__":
    main()
