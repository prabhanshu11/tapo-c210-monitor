"""SD card recording synchronization for TAPO C210."""

import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable
from pytapo import Tapo
from pytapo.media_stream.downloader import Downloader


class RecordingSync:
    """Synchronize recordings from TAPO C210 SD card to local storage."""

    def __init__(
        self,
        tapo: Tapo,
        output_dir: str | Path,
        window_size: int = 50,
    ):
        """Initialize recording sync.

        Args:
            tapo: Connected Tapo instance
            output_dir: Directory to save recordings
            window_size: Download window size (pytapo parameter)
        """
        self.tapo = tapo
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.window_size = window_size
        self._progress_callback: Callable[[str, float], None] | None = None

    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """Set callback for download progress updates.

        Args:
            callback: Function(filename, progress_percent)
        """
        self._progress_callback = callback

    def get_recordings_for_date(self, date: str | datetime) -> list[dict]:
        """Get list of recordings for a specific date.

        Args:
            date: Date as YYYYMMDD string or datetime object

        Returns:
            List of recording metadata dictionaries
        """
        if isinstance(date, datetime):
            date = date.strftime("%Y%m%d")

        try:
            recordings = self.tapo.getRecordings(date)
            return recordings if recordings else []
        except Exception as e:
            print(f"Failed to get recordings for {date}: {e}")
            return []

    def get_recordings_for_range(
        self,
        start_date: datetime,
        end_date: datetime | None = None,
    ) -> dict[str, list[dict]]:
        """Get recordings for a date range.

        Args:
            start_date: Start date
            end_date: End date (defaults to today)

        Returns:
            Dictionary mapping date strings to recording lists
        """
        if end_date is None:
            end_date = datetime.now()

        result = {}
        current = start_date

        while current <= end_date:
            date_str = current.strftime("%Y%m%d")
            recordings = self.get_recordings_for_date(date_str)
            if recordings:
                result[date_str] = recordings
            current += timedelta(days=1)

        return result

    def download_recording(
        self,
        recording: dict,
        output_filename: str | None = None,
    ) -> Path | None:
        """Download a single recording.

        Args:
            recording: Recording metadata from getRecordings()
            output_filename: Custom output filename (auto-generated if None)

        Returns:
            Path to downloaded file or None if failed
        """
        try:
            start_time = recording.get("startTime", "")
            end_time = recording.get("endTime", "")

            if output_filename is None:
                # Generate filename from timestamp
                output_filename = f"recording_{start_time}_{end_time}.mp4"

            output_path = self.output_dir / output_filename

            # Skip if already downloaded
            if output_path.exists():
                print(f"Recording already exists: {output_path}")
                return output_path

            # Use pytapo downloader
            downloader = Downloader(
                self.tapo,
                start_time,
                end_time,
                str(self.output_dir),
                fileName=output_filename,
                window_size=self.window_size,
            )

            # Download with progress updates
            async def do_download():
                await downloader.download()

            import asyncio
            asyncio.run(do_download())

            if output_path.exists():
                return output_path
            return None

        except Exception as e:
            print(f"Failed to download recording: {e}")
            return None

    def sync_date(
        self,
        date: str | datetime,
        skip_existing: bool = True,
    ) -> list[Path]:
        """Download all recordings for a specific date.

        Args:
            date: Date to sync
            skip_existing: Skip files that already exist

        Returns:
            List of downloaded file paths
        """
        if isinstance(date, datetime):
            date_str = date.strftime("%Y%m%d")
        else:
            date_str = date

        recordings = self.get_recordings_for_date(date_str)
        if not recordings:
            print(f"No recordings found for {date_str}")
            return []

        downloaded = []
        date_dir = self.output_dir / date_str
        date_dir.mkdir(exist_ok=True)

        for i, recording in enumerate(recordings):
            print(f"Downloading recording {i + 1}/{len(recordings)} for {date_str}")

            start_time = recording.get("startTime", str(i))
            filename = f"{date_str}_{start_time}.mp4"

            if skip_existing and (date_dir / filename).exists():
                print(f"  Skipping existing: {filename}")
                downloaded.append(date_dir / filename)
                continue

            result = self.download_recording(
                recording,
                output_filename=str(date_dir / filename),
            )
            if result:
                downloaded.append(result)

        return downloaded

    def sync_recent(self, days: int = 7) -> dict[str, list[Path]]:
        """Sync recordings from recent days.

        Args:
            days: Number of days to sync

        Returns:
            Dictionary mapping dates to downloaded file paths
        """
        result = {}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y%m%d")
            downloaded = self.sync_date(date_str)
            if downloaded:
                result[date_str] = downloaded
            current += timedelta(days=1)

        return result

    def get_storage_info(self) -> dict:
        """Get SD card storage information.

        Returns:
            Storage info dictionary
        """
        try:
            # This may require specific API call depending on pytapo version
            info = self.tapo.getBasicInfo()
            return {
                "available": True,
                "basic_info": info,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def list_local_recordings(self) -> list[Path]:
        """List all locally synced recordings.

        Returns:
            List of recording file paths
        """
        recordings = []
        for path in self.output_dir.rglob("*.mp4"):
            recordings.append(path)
        return sorted(recordings)

    def get_sync_status(self) -> dict:
        """Get synchronization status.

        Returns:
            Status dictionary with local and remote recording counts
        """
        local_recordings = self.list_local_recordings()

        # Get today's recordings from camera
        today = datetime.now().strftime("%Y%m%d")
        remote_today = self.get_recordings_for_date(today)

        return {
            "local_count": len(local_recordings),
            "local_size_mb": sum(p.stat().st_size for p in local_recordings) / (1024 * 1024),
            "remote_today_count": len(remote_today),
            "output_dir": str(self.output_dir),
        }
