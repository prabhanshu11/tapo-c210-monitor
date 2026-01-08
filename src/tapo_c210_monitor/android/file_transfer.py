"""File transfer utilities for Android sandbox data extraction."""

import subprocess
import time
from pathlib import Path
from typing import Generator
from dataclasses import dataclass


@dataclass
class RemoteFile:
    """Represents a file on the Android device."""
    path: str
    name: str
    size: int
    modified: str
    is_dir: bool


class FileTransfer:
    """Transfer files between Android device and local machine via ADB."""

    # Common paths for Tapo app data
    TAPO_DATA_PATHS = {
        "app_data": "/data/data/com.tplink.iot",
        "external_storage": "/sdcard/Android/data/com.tplink.iot",
        "media": "/sdcard/DCIM/Tapo",
        "downloads": "/sdcard/Download",
        "pictures": "/sdcard/Pictures",
        "movies": "/sdcard/Movies",
    }

    def __init__(self, controller: "AndroidController"):
        """Initialize file transfer.

        Args:
            controller: AndroidController instance
        """
        self.controller = controller

    def list_directory(self, remote_path: str) -> list[RemoteFile]:
        """List files in remote directory.

        Args:
            remote_path: Path on Android device

        Returns:
            List of RemoteFile objects
        """
        output = self.controller.shell(f"ls -la {remote_path}")
        files = []

        for line in output.strip().split("\n"):
            if not line or line.startswith("total"):
                continue

            parts = line.split()
            if len(parts) < 8:
                continue

            # Parse ls -la output
            # drwxr-xr-x  2 root root 4096 Jan  1 00:00 dirname
            perms = parts[0]
            size = int(parts[4]) if parts[4].isdigit() else 0
            modified = " ".join(parts[5:8])
            name = " ".join(parts[8:])

            if name in (".", ".."):
                continue

            files.append(RemoteFile(
                path=f"{remote_path}/{name}",
                name=name,
                size=size,
                modified=modified,
                is_dir=perms.startswith("d"),
            ))

        return files

    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists on device.

        Args:
            remote_path: Path on device

        Returns:
            True if file exists
        """
        output = self.controller.shell(f"test -e {remote_path} && echo EXISTS")
        return "EXISTS" in output

    def get_file_size(self, remote_path: str) -> int:
        """Get file size in bytes.

        Args:
            remote_path: Path on device

        Returns:
            File size in bytes, -1 if not found
        """
        output = self.controller.shell(f"stat -c %s {remote_path} 2>/dev/null")
        try:
            return int(output.strip())
        except ValueError:
            return -1

    def pull_file(
        self,
        remote_path: str,
        local_path: str | Path,
        progress_callback: callable = None,
    ) -> bool:
        """Pull file from device to local machine.

        Args:
            remote_path: Source path on device
            local_path: Destination local path
            progress_callback: Optional callback(bytes_transferred, total_bytes)

        Returns:
            True if transfer successful
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                ["adb", "-s", self.controller.device_serial, "pull", remote_path, str(local_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout for large files
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"Transfer timed out: {remote_path}")
            return False
        except Exception as e:
            print(f"Transfer failed: {e}")
            return False

    def push_file(
        self,
        local_path: str | Path,
        remote_path: str,
    ) -> bool:
        """Push file from local machine to device.

        Args:
            local_path: Source local path
            remote_path: Destination path on device

        Returns:
            True if transfer successful
        """
        local_path = Path(local_path)
        if not local_path.exists():
            print(f"Local file not found: {local_path}")
            return False

        try:
            result = subprocess.run(
                ["adb", "-s", self.controller.device_serial, "push", str(local_path), remote_path],
                capture_output=True,
                text=True,
                timeout=300,
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Push failed: {e}")
            return False

    def pull_directory(
        self,
        remote_path: str,
        local_path: str | Path,
        recursive: bool = True,
    ) -> list[Path]:
        """Pull entire directory from device.

        Args:
            remote_path: Source directory on device
            local_path: Destination local directory
            recursive: Include subdirectories

        Returns:
            List of pulled file paths
        """
        local_path = Path(local_path)
        local_path.mkdir(parents=True, exist_ok=True)

        pulled = []
        files = self.list_directory(remote_path)

        for f in files:
            dest = local_path / f.name

            if f.is_dir and recursive:
                sub_pulled = self.pull_directory(f.path, dest, recursive=True)
                pulled.extend(sub_pulled)
            elif not f.is_dir:
                if self.pull_file(f.path, dest):
                    pulled.append(dest)

        return pulled

    def find_files(
        self,
        remote_path: str,
        pattern: str = "*",
        max_depth: int = 3,
    ) -> list[str]:
        """Find files matching pattern on device.

        Args:
            remote_path: Directory to search
            pattern: Filename pattern (glob-style)
            max_depth: Maximum search depth

        Returns:
            List of matching file paths
        """
        output = self.controller.shell(
            f"find {remote_path} -maxdepth {max_depth} -name '{pattern}' -type f 2>/dev/null"
        )
        return [p.strip() for p in output.split("\n") if p.strip()]

    def get_tapo_media_files(self) -> list[str]:
        """Find all media files saved by Tapo app.

        Returns:
            List of media file paths on device
        """
        media_files = []

        # Check common Tapo media locations
        for name, path in self.TAPO_DATA_PATHS.items():
            if name in ("media", "pictures", "movies", "downloads"):
                files = self.find_files(path, "*.mp4", max_depth=5)
                media_files.extend(files)
                files = self.find_files(path, "*.jpg", max_depth=5)
                media_files.extend(files)

        return media_files

    def sync_tapo_media(
        self,
        local_dir: str | Path,
        delete_after_sync: bool = False,
    ) -> list[Path]:
        """Sync all Tapo media files to local directory.

        Args:
            local_dir: Local destination directory
            delete_after_sync: Delete files from device after successful sync

        Returns:
            List of synced local paths
        """
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        media_files = self.get_tapo_media_files()
        synced = []

        for remote_path in media_files:
            # Preserve some directory structure
            filename = Path(remote_path).name
            local_path = local_dir / filename

            # Skip if already exists with same size
            if local_path.exists():
                remote_size = self.get_file_size(remote_path)
                if local_path.stat().st_size == remote_size:
                    print(f"Skipping existing: {filename}")
                    synced.append(local_path)
                    continue

            print(f"Syncing: {filename}")
            if self.pull_file(remote_path, local_path):
                synced.append(local_path)
                if delete_after_sync:
                    self.controller.shell(f"rm {remote_path}")

        return synced

    def get_app_databases(self, package: str = "com.tplink.iot") -> list[str]:
        """Find app database files (requires root).

        Args:
            package: App package name

        Returns:
            List of database file paths
        """
        db_path = f"/data/data/{package}/databases"
        return self.find_files(db_path, "*.db", max_depth=1)

    def get_app_shared_prefs(self, package: str = "com.tplink.iot") -> list[str]:
        """Find app shared preferences files (requires root).

        Args:
            package: App package name

        Returns:
            List of shared prefs file paths
        """
        prefs_path = f"/data/data/{package}/shared_prefs"
        return self.find_files(prefs_path, "*.xml", max_depth=1)

    def extract_app_data(
        self,
        local_dir: str | Path,
        package: str = "com.tplink.iot",
    ) -> dict:
        """Extract all accessible app data (non-root accessible).

        Args:
            local_dir: Local destination directory
            package: App package name

        Returns:
            Dictionary mapping data types to extracted file paths
        """
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        extracted = {
            "external_storage": [],
            "media": [],
        }

        # External storage (accessible without root)
        ext_path = f"/sdcard/Android/data/{package}"
        if self.file_exists(ext_path):
            files = self.pull_directory(ext_path, local_dir / "external_storage")
            extracted["external_storage"] = files

        # Media files
        media = self.sync_tapo_media(local_dir / "media")
        extracted["media"] = media

        return extracted

    def watch_directory(
        self,
        remote_path: str,
        local_path: str | Path,
        poll_interval: float = 5.0,
    ) -> Generator[Path, None, None]:
        """Watch remote directory for new files and sync them.

        Args:
            remote_path: Directory to watch on device
            local_path: Local sync destination
            poll_interval: Seconds between checks

        Yields:
            Path to each newly synced file
        """
        local_path = Path(local_path)
        local_path.mkdir(parents=True, exist_ok=True)
        known_files = set()

        # Initial scan
        for f in self.list_directory(remote_path):
            if not f.is_dir:
                known_files.add(f.path)

        while True:
            time.sleep(poll_interval)

            try:
                current_files = self.list_directory(remote_path)
            except Exception as e:
                print(f"Watch error: {e}")
                continue

            for f in current_files:
                if f.is_dir or f.path in known_files:
                    continue

                # New file found
                known_files.add(f.path)
                dest = local_path / f.name

                print(f"New file detected: {f.name}")
                if self.pull_file(f.path, dest):
                    yield dest

    def get_storage_stats(self) -> dict:
        """Get device storage statistics.

        Returns:
            Storage information dictionary
        """
        output = self.controller.shell("df -h /sdcard")
        lines = output.strip().split("\n")

        if len(lines) < 2:
            return {"error": "Could not get storage info"}

        # Parse df output
        parts = lines[1].split()
        if len(parts) >= 4:
            return {
                "total": parts[1],
                "used": parts[2],
                "available": parts[3],
                "use_percent": parts[4] if len(parts) > 4 else "unknown",
            }

        return {"raw": output}
