"""SQLite storage for object detection results.

Follows datalake conventions: FTS5 for text search, ISO timestamps,
source_device tagging, Unix timestamps for time queries.
"""

import sqlite3
import time
import json
from pathlib import Path
from typing import Optional

from .yolo_detector import Detection


class ObjectLogger:
    """Logs detection scans and individual objects to SQLite."""

    def __init__(self, db_path: str | Path = "data/object_detections.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()

        cur.executescript("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_type TEXT NOT NULL,
                source_device TEXT NOT NULL,
                source_camera TEXT NOT NULL,
                frame_timestamp_unix INTEGER NOT NULL,
                frame_path TEXT,
                frame_width INTEGER,
                frame_height INTEGER,
                model_name TEXT NOT NULL,
                objects_count INTEGER DEFAULT 0,
                change_score REAL,
                llm_summary TEXT,
                tags TEXT,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                metadata TEXT
            );

            CREATE TABLE IF NOT EXISTS objects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                class_name TEXT NOT NULL,
                class_id INTEGER,
                confidence REAL NOT NULL,
                bbox_x1 INTEGER,
                bbox_y1 INTEGER,
                bbox_x2 INTEGER,
                bbox_y2 INTEGER,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            );

            CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(frame_timestamp_unix DESC);
            CREATE INDEX IF NOT EXISTS idx_scans_camera ON scans(source_camera);
            CREATE INDEX IF NOT EXISTS idx_scans_created ON scans(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_scans_type ON scans(scan_type);
            CREATE INDEX IF NOT EXISTS idx_objects_class ON objects(class_name);
            CREATE INDEX IF NOT EXISTS idx_objects_scan ON objects(scan_id);
        """)

        # Migrate scans table: add columns for PTZ + frame retention
        self._migrate_scans_table(cur)

        # New tables for temporal tracking
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS object_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                track_status TEXT NOT NULL DEFAULT 'active',
                first_seen_unix INTEGER NOT NULL,
                last_seen_unix INTEGER NOT NULL,
                first_scan_id INTEGER REFERENCES scans(id),
                last_scan_id INTEGER REFERENCES scans(id),
                total_detections INTEGER DEFAULT 1,
                avg_confidence REAL,
                last_bbox_x1 INTEGER, last_bbox_y1 INTEGER,
                last_bbox_x2 INTEGER, last_bbox_y2 INTEGER,
                camera_pan REAL,
                camera_tilt REAL,
                consecutive_misses INTEGER DEFAULT 0,
                departed_at_unix INTEGER,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            );

            CREATE INDEX IF NOT EXISTS idx_tracks_status ON object_tracks(track_status);
            CREATE INDEX IF NOT EXISTS idx_tracks_class ON object_tracks(class_name);
            CREATE INDEX IF NOT EXISTS idx_tracks_last_seen ON object_tracks(last_seen_unix DESC);

            CREATE TABLE IF NOT EXISTS edge_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER REFERENCES scans(id),
                case_type TEXT NOT NULL,
                class_name TEXT,
                confidence REAL,
                description TEXT,
                frame_path TEXT,
                resolved INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            );

            CREATE TABLE IF NOT EXISTS coverage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_pan REAL NOT NULL,
                camera_tilt REAL NOT NULL,
                scanned_at_unix INTEGER NOT NULL,
                objects_found INTEGER DEFAULT 0,
                interesting INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_coverage_time ON coverage_log(scanned_at_unix DESC);
        """)

        # FTS5 for searching LLM descriptions and tags
        existing = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='scans_fts'"
        ).fetchone()

        if not existing:
            cur.executescript("""
                CREATE VIRTUAL TABLE scans_fts USING fts5(
                    llm_summary, tags,
                    content='scans', content_rowid='id'
                );

                CREATE TRIGGER scans_ai AFTER INSERT ON scans BEGIN
                    INSERT INTO scans_fts(rowid, llm_summary, tags)
                    VALUES (new.id, new.llm_summary, new.tags);
                END;

                CREATE TRIGGER scans_ad AFTER DELETE ON scans BEGIN
                    INSERT INTO scans_fts(scans_fts, rowid, llm_summary, tags)
                    VALUES ('delete', old.id, old.llm_summary, old.tags);
                END;

                CREATE TRIGGER scans_au AFTER UPDATE ON scans BEGIN
                    INSERT INTO scans_fts(scans_fts, rowid, llm_summary, tags)
                    VALUES ('delete', old.id, old.llm_summary, old.tags);
                    INSERT INTO scans_fts(rowid, llm_summary, tags)
                    VALUES (new.id, new.llm_summary, new.tags);
                END;
            """)

        # Views
        cur.executescript("""
            CREATE VIEW IF NOT EXISTS v_current_scene AS
            SELECT s.id AS scan_id, s.frame_timestamp_unix, s.model_name,
                   s.objects_count, s.llm_summary, s.created_at,
                   o.class_name, o.confidence, o.bbox_x1, o.bbox_y1,
                   o.bbox_x2, o.bbox_y2
            FROM scans s
            LEFT JOIN objects o ON o.scan_id = s.id
            WHERE s.id = (SELECT MAX(id) FROM scans);

            CREATE VIEW IF NOT EXISTS v_object_timeline AS
            SELECT o.class_name,
                   s.frame_timestamp_unix,
                   s.created_at,
                   o.confidence,
                   s.scan_type,
                   s.source_camera
            FROM objects o
            JOIN scans s ON s.id = o.scan_id
            ORDER BY s.frame_timestamp_unix DESC;

            CREATE VIEW IF NOT EXISTS v_active_tracks AS
            SELECT id, class_name, first_seen_unix, last_seen_unix,
                   (last_seen_unix - first_seen_unix) as duration_seconds,
                   total_detections, avg_confidence, camera_pan, camera_tilt
            FROM object_tracks
            WHERE track_status = 'active'
            ORDER BY last_seen_unix DESC;
        """)

        self.conn.commit()

    def _migrate_scans_table(self, cur: sqlite3.Cursor):
        """Add new columns to scans table if they don't exist yet."""
        columns = {
            row[1] for row in cur.execute("PRAGMA table_info(scans)").fetchall()
        }
        migrations = [
            ("camera_pan", "REAL"),
            ("camera_tilt", "REAL"),
            ("frame_retained", "INTEGER DEFAULT 0"),
        ]
        for col_name, col_type in migrations:
            if col_name not in columns:
                cur.execute(f"ALTER TABLE scans ADD COLUMN {col_name} {col_type}")

    # ── Scan logging ──────────────────────────────────────────────

    def log_scan(
        self,
        scan_type: str,
        detections: list[Detection],
        model_name: str = "yolov8n",
        source_device: str = "desktop",
        source_camera: str = "tapo-c210-192.168.50.199",
        frame_path: Optional[str] = None,
        change_score: Optional[float] = None,
        llm_summary: Optional[str] = None,
        tags: Optional[str] = None,
        metadata: Optional[dict] = None,
        camera_pan: Optional[float] = None,
        camera_tilt: Optional[float] = None,
        frame_retained: bool = False,
    ) -> int:
        """Log a detection scan with all its objects.

        Returns:
            scan_id of the inserted row.
        """
        now_unix = int(time.time())
        frame_w = detections[0].frame_width if detections else None
        frame_h = detections[0].frame_height if detections else None

        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO scans
               (scan_type, source_device, source_camera, frame_timestamp_unix,
                frame_path, frame_width, frame_height, model_name,
                objects_count, change_score, llm_summary, tags, metadata,
                camera_pan, camera_tilt, frame_retained)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                scan_type, source_device, source_camera, now_unix,
                frame_path, frame_w, frame_h, model_name,
                len(detections), change_score, llm_summary, tags,
                json.dumps(metadata) if metadata else None,
                camera_pan, camera_tilt, int(frame_retained),
            ),
        )
        scan_id = cur.lastrowid

        for d in detections:
            cur.execute(
                """INSERT INTO objects
                   (scan_id, class_name, class_id, confidence,
                    bbox_x1, bbox_y1, bbox_x2, bbox_y2)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (scan_id, d.class_name, d.class_id, d.confidence,
                 d.bbox[0], d.bbox[1], d.bbox[2], d.bbox[3]),
            )

        self.conn.commit()
        return scan_id

    def update_llm_summary(self, scan_id: int, llm_summary: str):
        """Add or update the LLM summary for a scan."""
        self.conn.execute(
            "UPDATE scans SET llm_summary = ? WHERE id = ?",
            (llm_summary, scan_id),
        )
        self.conn.commit()

    def update_frame_retention(self, scan_id: int, frame_path: str, retained: bool):
        """Mark a scan's frame as retained and update its path."""
        self.conn.execute(
            "UPDATE scans SET frame_path = ?, frame_retained = ? WHERE id = ?",
            (frame_path, int(retained), scan_id),
        )
        self.conn.commit()

    # ── Object tracks ─────────────────────────────────────────────

    def upsert_track(
        self,
        class_name: str,
        scan_id: int,
        detection: Detection,
        camera_pan: Optional[float],
        camera_tilt: Optional[float],
    ) -> int:
        """Match detection to an active track or create a new one.

        Matching: same class_name + camera position within +/-0.2 pan/tilt.
        Returns track_id.
        """
        now = int(time.time())
        cur = self.conn.cursor()

        # Try to find a matching active track
        match = None
        if camera_pan is not None and camera_tilt is not None:
            match = cur.execute(
                """SELECT id, total_detections, avg_confidence
                   FROM object_tracks
                   WHERE class_name = ? AND track_status = 'active'
                     AND ABS(camera_pan - ?) < 0.2 AND ABS(camera_tilt - ?) < 0.2
                   ORDER BY last_seen_unix DESC LIMIT 1""",
                (class_name, camera_pan, camera_tilt),
            ).fetchone()
        else:
            # No camera position — match by class only (passive mode)
            match = cur.execute(
                """SELECT id, total_detections, avg_confidence
                   FROM object_tracks
                   WHERE class_name = ? AND track_status = 'active'
                     AND camera_pan IS NULL
                   ORDER BY last_seen_unix DESC LIMIT 1""",
                (class_name,),
            ).fetchone()

        if match:
            track_id = match[0]
            total = match[1] + 1
            # Running average
            new_avg = ((match[2] or 0) * match[1] + detection.confidence) / total
            cur.execute(
                """UPDATE object_tracks SET
                       last_seen_unix = ?, last_scan_id = ?,
                       total_detections = ?, avg_confidence = ?,
                       last_bbox_x1 = ?, last_bbox_y1 = ?,
                       last_bbox_x2 = ?, last_bbox_y2 = ?,
                       camera_pan = ?, camera_tilt = ?,
                       consecutive_misses = 0
                   WHERE id = ?""",
                (
                    now, scan_id, total, new_avg,
                    detection.bbox[0], detection.bbox[1],
                    detection.bbox[2], detection.bbox[3],
                    camera_pan, camera_tilt, track_id,
                ),
            )
        else:
            cur.execute(
                """INSERT INTO object_tracks
                   (class_name, track_status, first_seen_unix, last_seen_unix,
                    first_scan_id, last_scan_id, total_detections, avg_confidence,
                    last_bbox_x1, last_bbox_y1, last_bbox_x2, last_bbox_y2,
                    camera_pan, camera_tilt)
                   VALUES (?, 'active', ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    class_name, now, now, scan_id, scan_id, detection.confidence,
                    detection.bbox[0], detection.bbox[1],
                    detection.bbox[2], detection.bbox[3],
                    camera_pan, camera_tilt,
                ),
            )
            track_id = cur.lastrowid

        self.conn.commit()
        return track_id

    def mark_departed(self, track_id: int):
        """Set a track as departed."""
        now = int(time.time())
        self.conn.execute(
            "UPDATE object_tracks SET track_status = 'departed', departed_at_unix = ? WHERE id = ?",
            (now, track_id),
        )
        self.conn.commit()

    def increment_track_misses(self, camera_pan: Optional[float], camera_tilt: Optional[float]):
        """Increment misses for active tracks near this camera position.

        Auto-departs tracks with >3 consecutive misses at the same position.
        """
        cur = self.conn.cursor()
        now = int(time.time())

        if camera_pan is not None and camera_tilt is not None:
            rows = cur.execute(
                """SELECT id, consecutive_misses FROM object_tracks
                   WHERE track_status = 'active'
                     AND ABS(camera_pan - ?) < 0.2 AND ABS(camera_tilt - ?) < 0.2""",
                (camera_pan, camera_tilt),
            ).fetchall()
        else:
            rows = cur.execute(
                """SELECT id, consecutive_misses FROM object_tracks
                   WHERE track_status = 'active' AND camera_pan IS NULL""",
            ).fetchall()

        for row in rows:
            track_id, misses = row[0], row[1]
            new_misses = misses + 1
            if new_misses > 3:
                cur.execute(
                    "UPDATE object_tracks SET track_status = 'departed', departed_at_unix = ? WHERE id = ?",
                    (now, track_id),
                )
            else:
                cur.execute(
                    "UPDATE object_tracks SET consecutive_misses = ? WHERE id = ?",
                    (new_misses, track_id),
                )

        self.conn.commit()

    def get_active_tracks(self) -> list[dict]:
        """Get all currently active object tracks."""
        rows = self.conn.execute("SELECT * FROM v_active_tracks").fetchall()
        return [dict(r) for r in rows]

    def get_tracks_summary(self, hours: int = 24) -> list[dict]:
        """Get all tracks (active + departed) in the time window."""
        cutoff = int(time.time()) - (hours * 3600)
        rows = self.conn.execute(
            """SELECT id, class_name, track_status,
                      first_seen_unix, last_seen_unix,
                      (last_seen_unix - first_seen_unix) as duration_seconds,
                      total_detections, avg_confidence,
                      camera_pan, camera_tilt, departed_at_unix
               FROM object_tracks
               WHERE last_seen_unix > ? OR (departed_at_unix IS NOT NULL AND departed_at_unix > ?)
               ORDER BY first_seen_unix DESC""",
            (cutoff, cutoff),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Edge cases ────────────────────────────────────────────────

    def log_edge_case(
        self,
        scan_id: int,
        case_type: str,
        class_name: Optional[str] = None,
        confidence: Optional[float] = None,
        description: Optional[str] = None,
        frame_path: Optional[str] = None,
    ) -> int:
        """Log a detection quality issue for later review."""
        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO edge_cases
               (scan_id, case_type, class_name, confidence, description, frame_path)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (scan_id, case_type, class_name, confidence, description, frame_path),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_edge_cases(self, hours: int = 24, unresolved_only: bool = True) -> list[dict]:
        """Get edge cases in the time window."""
        cutoff = int(time.time()) - (hours * 3600)
        query = """SELECT e.*, s.frame_timestamp_unix
                   FROM edge_cases e
                   LEFT JOIN scans s ON s.id = e.scan_id
                   WHERE e.created_at > datetime(?, 'unixepoch')"""
        if unresolved_only:
            query += " AND e.resolved = 0"
        query += " ORDER BY e.id DESC"
        rows = self.conn.execute(query, (cutoff,)).fetchall()
        return [dict(r) for r in rows]

    # ── Coverage log ──────────────────────────────────────────────

    def log_coverage(
        self,
        camera_pan: float,
        camera_tilt: float,
        objects_found: int,
        interesting: bool = False,
    ):
        """Record that a PTZ position was scanned."""
        now = int(time.time())
        self.conn.execute(
            """INSERT INTO coverage_log
               (camera_pan, camera_tilt, scanned_at_unix, objects_found, interesting)
               VALUES (?, ?, ?, ?, ?)""",
            (camera_pan, camera_tilt, now, objects_found, int(interesting)),
        )
        self.conn.commit()

    def get_coverage_gaps(self, hours: int = 24) -> list[dict]:
        """Get positions not scanned recently.

        Returns all known positions with their last scan time,
        sorted by staleness (least recently scanned first).
        """
        cutoff = int(time.time()) - (hours * 3600)
        rows = self.conn.execute(
            """SELECT camera_pan, camera_tilt,
                      MAX(scanned_at_unix) as last_scanned,
                      SUM(objects_found) as total_objects,
                      COUNT(*) as scan_count
               FROM coverage_log
               GROUP BY ROUND(camera_pan, 1), ROUND(camera_tilt, 1)
               HAVING MAX(scanned_at_unix) < ? OR MAX(scanned_at_unix) IS NULL
               ORDER BY MAX(scanned_at_unix) ASC""",
            (cutoff,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Query methods (existing) ──────────────────────────────────

    def get_recent_scans(self, limit: int = 10) -> list[dict]:
        """Get the most recent scans with their object lists."""
        rows = self.conn.execute(
            """SELECT s.*, GROUP_CONCAT(o.class_name || ':' ||
               printf('%.2f', o.confidence)) AS object_list
               FROM scans s
               LEFT JOIN objects o ON o.scan_id = s.id
               GROUP BY s.id
               ORDER BY s.frame_timestamp_unix DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_objects_at_time(
        self, unix_ts: int, window_seconds: int = 60
    ) -> list[dict]:
        """Get all objects detected near a given timestamp."""
        rows = self.conn.execute(
            """SELECT o.class_name, o.confidence,
                      o.bbox_x1, o.bbox_y1, o.bbox_x2, o.bbox_y2,
                      s.frame_timestamp_unix, s.llm_summary
               FROM objects o
               JOIN scans s ON s.id = o.scan_id
               WHERE s.frame_timestamp_unix BETWEEN ? AND ?
               ORDER BY s.frame_timestamp_unix DESC""",
            (unix_ts - window_seconds, unix_ts + window_seconds),
        ).fetchall()
        return [dict(r) for r in rows]

    def search(self, query: str) -> list[dict]:
        """Full-text search across LLM summaries and tags."""
        rows = self.conn.execute(
            """SELECT s.*
               FROM scans_fts fts
               JOIN scans s ON s.id = fts.rowid
               WHERE scans_fts MATCH ?
               ORDER BY rank
               LIMIT 20""",
            (query,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_object_timeline(
        self, class_name: str, hours: int = 24
    ) -> list[dict]:
        """Get timeline of when a specific object class was detected."""
        cutoff = int(time.time()) - (hours * 3600)
        rows = self.conn.execute(
            """SELECT o.class_name, o.confidence,
                      s.frame_timestamp_unix, s.scan_type, s.source_camera
               FROM objects o
               JOIN scans s ON s.id = o.scan_id
               WHERE o.class_name = ? AND s.frame_timestamp_unix > ?
               ORDER BY s.frame_timestamp_unix DESC""",
            (class_name, cutoff),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_class_summary(self, hours: int = 24) -> list[dict]:
        """Get summary of all detected classes in the time window."""
        cutoff = int(time.time()) - (hours * 3600)
        rows = self.conn.execute(
            """SELECT o.class_name,
                      COUNT(*) as detection_count,
                      AVG(o.confidence) as avg_confidence,
                      MIN(s.frame_timestamp_unix) as first_seen,
                      MAX(s.frame_timestamp_unix) as last_seen
               FROM objects o
               JOIN scans s ON s.id = o.scan_id
               WHERE s.frame_timestamp_unix > ?
               GROUP BY o.class_name
               ORDER BY detection_count DESC""",
            (cutoff,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Summary query methods (for daily_summary) ─────────────────

    def get_scan_stats(self, hours: int = 24) -> dict:
        """Get scan statistics by type for the time window."""
        cutoff = int(time.time()) - (hours * 3600)
        rows = self.conn.execute(
            """SELECT scan_type, COUNT(*) as count
               FROM scans WHERE frame_timestamp_unix > ?
               GROUP BY scan_type ORDER BY count DESC""",
            (cutoff,),
        ).fetchall()
        return {r["scan_type"]: r["count"] for r in rows}

    def get_recent_llm_summaries(self, hours: int = 24) -> list[dict]:
        """Get scans that have LLM summaries in the time window."""
        cutoff = int(time.time()) - (hours * 3600)
        rows = self.conn.execute(
            """SELECT id, frame_timestamp_unix, scan_type, llm_summary
               FROM scans
               WHERE frame_timestamp_unix > ? AND llm_summary IS NOT NULL
               ORDER BY frame_timestamp_unix DESC""",
            (cutoff,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Lifecycle ─────────────────────────────────────────────────

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
