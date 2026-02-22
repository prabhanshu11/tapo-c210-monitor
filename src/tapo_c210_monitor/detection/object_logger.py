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

        # FTS5 for searching LLM descriptions and tags
        # Check if it already exists to avoid error on re-init
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
        """)

        self.conn.commit()

    def log_scan(
        self,
        scan_type: str,
        detections: list[Detection],
        model_name: str = "yolov8n",
        source_device: str = "desktop",
        source_camera: str = "tapo-c210-192.168.29.183",
        frame_path: Optional[str] = None,
        change_score: Optional[float] = None,
        llm_summary: Optional[str] = None,
        tags: Optional[str] = None,
        metadata: Optional[dict] = None,
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
                objects_count, change_score, llm_summary, tags, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                scan_type, source_device, source_camera, now_unix,
                frame_path, frame_w, frame_h, model_name,
                len(detections), change_score, llm_summary, tags,
                json.dumps(metadata) if metadata else None,
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

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
