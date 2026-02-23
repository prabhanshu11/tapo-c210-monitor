"""Frame retention policy for detection scans.

Copies interesting frames to date-organized storage and manages cleanup
of routine/expired frames.
"""

import shutil
import time
from pathlib import Path

from .object_logger import ObjectLogger


class FrameStore:
    """Manages frame storage with time-based retention."""

    def __init__(
        self,
        base_dir: str | Path = "data/frames",
        retention_hours: int = 168,  # 7 days
    ):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.retention_hours = retention_hours

    def store(self, source_path: str, scan_id: int) -> str:
        """Copy a frame to date-organized retention storage.

        Returns:
            Path to the stored frame.
        """
        date_str = time.strftime("%Y-%m-%d")
        day_dir = self.base_dir / date_str
        day_dir.mkdir(parents=True, exist_ok=True)

        src = Path(source_path)
        suffix = src.suffix or ".jpg"
        dest = day_dir / f"scan_{scan_id}{suffix}"
        shutil.copy2(str(src), str(dest))
        return str(dest)

    def cleanup(self, logger: ObjectLogger):
        """Delete frames based on retention policy.

        - Non-retained frames older than 1 hour: delete
        - Retained frames older than retention_hours: delete
        """
        now = int(time.time())
        one_hour_ago = now - 3600
        retention_cutoff = now - (self.retention_hours * 3600)

        # Delete non-retained frames older than 1 hour
        rows = logger.conn.execute(
            """SELECT id, frame_path FROM scans
               WHERE frame_retained = 0 AND frame_path IS NOT NULL
                 AND frame_timestamp_unix < ?""",
            (one_hour_ago,),
        ).fetchall()

        deleted = 0
        for row in rows:
            p = Path(row["frame_path"])
            if p.exists():
                p.unlink()
                deleted += 1

        # Delete retained frames past retention window
        old_rows = logger.conn.execute(
            """SELECT id, frame_path FROM scans
               WHERE frame_retained = 1 AND frame_path IS NOT NULL
                 AND frame_timestamp_unix < ?""",
            (retention_cutoff,),
        ).fetchall()

        for row in old_rows:
            p = Path(row["frame_path"])
            if p.exists():
                p.unlink()
                deleted += 1

        # Clean up empty date directories
        if self.base_dir.exists():
            for day_dir in self.base_dir.iterdir():
                if day_dir.is_dir() and not any(day_dir.iterdir()):
                    day_dir.rmdir()

        if deleted:
            print(f"[FrameStore] Cleaned up {deleted} expired frames")
