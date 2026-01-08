"""Session management for Android automation with structured logging."""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class SessionEvent:
    """Represents a logged event in a session."""

    def __init__(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        success: bool = True,
        error: str | None = None,
    ):
        self.timestamp = datetime.now().isoformat()
        self.event_type = event_type
        self.data = data or {}
        self.success = success
        self.error = error

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "data": self.data,
            "success": self.success,
            "error": self.error,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class Session:
    """Manages an automation session with logging and state tracking."""

    def __init__(
        self,
        name: str,
        base_dir: Path | str = "sessions",
    ):
        """Initialize a new session.

        Args:
            name: Short name for the session (e.g., "install-tapo")
            base_dir: Base directory for session storage
        """
        self.name = name
        self.base_dir = Path(base_dir)
        self.start_time = datetime.now()
        self.session_id = self.start_time.strftime("%Y-%m-%d_%H-%M-%S") + f"_{name}"

        # Create session directory structure
        self.session_dir = self.base_dir / self.session_id
        self.screenshots_dir = self.session_dir / "screenshots"
        self.ui_dumps_dir = self.session_dir / "ui_dumps"

        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.ui_dumps_dir.mkdir(exist_ok=True)

        # Files
        self.events_file = self.session_dir / "events.jsonl"
        self.metadata_file = self.session_dir / "session.json"
        self.summary_file = self.session_dir / "summary.md"

        # State tracking
        self.events: list[SessionEvent] = []
        self.screenshot_count = 0
        self.ui_dump_count = 0
        self.error_count = 0
        self.end_time: datetime | None = None
        self.status = "running"

        # Initialize metadata
        self._write_metadata()
        self.log_event("session_start", {"name": name, "session_id": self.session_id})

    def _write_metadata(self) -> None:
        """Write session metadata to file."""
        metadata = {
            "session_id": self.session_id,
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "screenshot_count": self.screenshot_count,
            "ui_dump_count": self.ui_dump_count,
            "error_count": self.error_count,
            "event_count": len(self.events),
        }
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    def log_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        success: bool = True,
        error: str | None = None,
    ) -> SessionEvent:
        """Log an event to the session.

        Args:
            event_type: Type of event (e.g., "tap", "screenshot", "error")
            data: Additional event data
            success: Whether the operation succeeded
            error: Error message if failed

        Returns:
            The created event
        """
        event = SessionEvent(event_type, data, success, error)
        self.events.append(event)

        if not success:
            self.error_count += 1

        # Append to events file (JSONL format)
        with open(self.events_file, "a") as f:
            f.write(event.to_json() + "\n")

        return event

    def save_screenshot(self, source_path: Path | str) -> Path:
        """Save a screenshot to the session directory.

        Args:
            source_path: Path to the screenshot file

        Returns:
            Path to saved screenshot in session directory
        """
        self.screenshot_count += 1
        dest_name = f"{self.screenshot_count:03d}.png"
        dest_path = self.screenshots_dir / dest_name

        shutil.copy(source_path, dest_path)
        self.log_event("screenshot", {"path": str(dest_path), "index": self.screenshot_count})

        return dest_path

    def save_ui_dump(self, source_path: Path | str) -> Path:
        """Save a UI hierarchy dump to the session directory.

        Args:
            source_path: Path to the UI dump XML file

        Returns:
            Path to saved dump in session directory
        """
        self.ui_dump_count += 1
        dest_name = f"{self.ui_dump_count:03d}.xml"
        dest_path = self.ui_dumps_dir / dest_name

        shutil.copy(source_path, dest_path)
        self.log_event("ui_dump", {"path": str(dest_path), "index": self.ui_dump_count})

        return dest_path

    def log_adb_command(
        self,
        command: str,
        output: str | None = None,
        return_code: int = 0,
        error: str | None = None,
    ) -> None:
        """Log an ADB command execution.

        Args:
            command: The ADB command executed
            output: Command output
            return_code: Exit code
            error: Error message if failed
        """
        self.log_event(
            "adb_command",
            {
                "command": command,
                "output": output[:500] if output and len(output) > 500 else output,
                "return_code": return_code,
            },
            success=return_code == 0,
            error=error,
        )

    def log_emulator_event(
        self,
        event_type: str,
        details: dict[str, Any] | None = None,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Log an emulator lifecycle event.

        Args:
            event_type: Type (start, stop, crash, reconnect)
            details: Additional details
            success: Whether successful
            error: Error message
        """
        self.log_event(
            f"emulator_{event_type}",
            details,
            success=success,
            error=error,
        )

    def end(self, status: str = "completed") -> None:
        """End the session and generate summary.

        Args:
            status: Final status (completed, failed, aborted)
        """
        self.end_time = datetime.now()
        self.status = status
        self.log_event("session_end", {"status": status})
        self._write_metadata()
        self._generate_summary()

    def _generate_summary(self) -> None:
        """Generate a markdown summary of the session."""
        duration = (self.end_time or datetime.now()) - self.start_time
        duration_str = str(duration).split(".")[0]  # Remove microseconds

        # Count event types
        event_types: dict[str, int] = {}
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1

        # Get errors
        errors = [e for e in self.events if not e.success]

        summary = f"""# Session Summary: {self.name}

## Overview
- **Session ID**: {self.session_id}
- **Status**: {self.status}
- **Duration**: {duration_str}
- **Start**: {self.start_time.strftime("%Y-%m-%d %H:%M:%S")}
- **End**: {self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else "N/A"}

## Statistics
- **Total Events**: {len(self.events)}
- **Screenshots**: {self.screenshot_count}
- **UI Dumps**: {self.ui_dump_count}
- **Errors**: {self.error_count}

## Event Breakdown
| Event Type | Count |
|------------|-------|
"""
        for event_type, count in sorted(event_types.items()):
            summary += f"| {event_type} | {count} |\n"

        if errors:
            summary += "\n## Errors\n"
            for i, error in enumerate(errors, 1):
                summary += f"\n### Error {i}: {error.event_type}\n"
                summary += f"- **Time**: {error.timestamp}\n"
                summary += f"- **Error**: {error.error or 'Unknown'}\n"
                if error.data:
                    summary += f"- **Data**: {json.dumps(error.data, indent=2)}\n"

        summary += f"\n## Files\n"
        summary += f"- Events log: `events.jsonl`\n"
        summary += f"- Screenshots: `screenshots/` ({self.screenshot_count} files)\n"
        summary += f"- UI Dumps: `ui_dumps/` ({self.ui_dump_count} files)\n"

        with open(self.summary_file, "w") as f:
            f.write(summary)


class SessionManager:
    """Manages multiple automation sessions."""

    def __init__(self, base_dir: Path | str = "sessions"):
        """Initialize session manager.

        Args:
            base_dir: Base directory for all sessions
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Session | None = None

    def start_session(self, name: str) -> Session:
        """Start a new session.

        Args:
            name: Session name

        Returns:
            The new session
        """
        if self.current_session and self.current_session.status == "running":
            self.current_session.end("aborted")

        self.current_session = Session(name, self.base_dir)
        return self.current_session

    def end_session(self, status: str = "completed") -> None:
        """End the current session.

        Args:
            status: Final status
        """
        if self.current_session:
            self.current_session.end(status)
            self.current_session = None

    def list_sessions(self) -> list[dict]:
        """List all sessions.

        Returns:
            List of session metadata dictionaries
        """
        sessions = []
        for session_dir in sorted(self.base_dir.iterdir()):
            if session_dir.is_dir():
                metadata_file = session_dir / "session.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        sessions.append(json.load(f))
        return sessions

    def get_session(self, session_id: str) -> dict | None:
        """Get session metadata by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session metadata or None
        """
        session_dir = self.base_dir / session_id
        metadata_file = session_dir / "session.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        return None
