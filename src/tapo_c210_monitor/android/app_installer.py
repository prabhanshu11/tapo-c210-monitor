"""APK installation module with multiple strategies.

Supports:
- Direct APK installation from local files
- Split APK installation for app bundles (install-multiple)
- APK download from mirrors (APKMirror, APKPure)
- Package verification and version checking
"""

import hashlib
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

import httpx

from .session import Session


class InstallMethod(Enum):
    """APK installation methods."""
    DIRECT = "direct"           # Single APK file
    SPLIT = "split"             # Multiple APK files (App Bundle)
    STREAMING = "streaming"     # Stream from URL directly


class InstallResult(Enum):
    """Installation result status."""
    SUCCESS = "success"
    ALREADY_INSTALLED = "already_installed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    DOWNLOAD_FAILED = "download_failed"
    VERIFICATION_FAILED = "verification_failed"


@dataclass
class APKSource:
    """Represents an APK download source."""
    name: str
    base_url: str
    # Function to construct download URL from package name
    url_builder: Callable[[str], str] | None = None
    requires_scraping: bool = False
    priority: int = 0  # Lower = higher priority


@dataclass
class InstallStatus:
    """Result of an installation attempt."""
    result: InstallResult
    method: InstallMethod | None = None
    version_installed: str | None = None
    error: str | None = None
    duration_seconds: float = 0.0


class AppInstaller:
    """Handles APK installation with multiple fallback strategies."""

    # Common APK sources
    DEFAULT_SOURCES = [
        APKSource(
            name="apkpure",
            base_url="https://apkpure.com",
            requires_scraping=True,
            priority=1,
        ),
        APKSource(
            name="apkmirror",
            base_url="https://www.apkmirror.com",
            requires_scraping=True,
            priority=2,
        ),
    ]

    def __init__(
        self,
        device_serial: str | None = None,
        session: Session | None = None,
        download_dir: Path | str | None = None,
        max_retries: int = 3,
    ):
        """Initialize app installer.

        Args:
            device_serial: Target device serial (None for default)
            session: Session for logging
            download_dir: Directory for downloaded APKs
            max_retries: Maximum retry attempts per method
        """
        self.device_serial = device_serial
        self.session = session
        self.download_dir = Path(download_dir) if download_dir else Path(tempfile.gettempdir()) / "apk_downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self.sources = self.DEFAULT_SOURCES.copy()

    def _log(self, event_type: str, data: dict | None = None, success: bool = True, error: str | None = None) -> None:
        """Log event to session if available."""
        if self.session:
            self.session.log_event(f"installer_{event_type}", data, success, error)
        status = "OK" if success else "FAIL"
        print(f"[AppInstaller] {event_type} [{status}]: {data or ''} {error or ''}")

    def _adb(self, *args: str, timeout: int = 120) -> tuple[int, str, str]:
        """Run ADB command.

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = ["adb"]
        if self.device_serial:
            cmd.extend(["-s", self.device_serial])
        cmd.extend(args)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except FileNotFoundError:
            return -1, "", "ADB not found"

    def get_installed_version(self, package: str) -> str | None:
        """Get installed version of a package.

        Args:
            package: Package name (e.g., com.tplink.iot)

        Returns:
            Version string or None if not installed
        """
        code, stdout, _ = self._adb("shell", f"dumpsys package {package} | grep versionName")
        if code == 0 and stdout.strip():
            # Parse: versionName=1.2.3
            match = re.search(r"versionName=([^\s]+)", stdout)
            if match:
                return match.group(1)
        return None

    def is_installed(self, package: str) -> bool:
        """Check if package is installed.

        Args:
            package: Package name

        Returns:
            True if installed
        """
        code, stdout, _ = self._adb("shell", f"pm list packages | grep {package}")
        return code == 0 and package in stdout

    def uninstall(self, package: str) -> bool:
        """Uninstall a package.

        Args:
            package: Package name

        Returns:
            True if successful
        """
        self._log("uninstall_start", {"package": package})
        code, _, stderr = self._adb("uninstall", package)
        success = code == 0
        self._log("uninstall_complete", {"package": package}, success=success, error=stderr if not success else None)
        return success

    def install_apk(self, apk_path: Path | str, reinstall: bool = False) -> InstallStatus:
        """Install a single APK file.

        Args:
            apk_path: Path to APK file
            reinstall: Allow reinstall/downgrade

        Returns:
            Installation status
        """
        apk_path = Path(apk_path)
        if not apk_path.exists():
            return InstallStatus(InstallResult.FAILED, error=f"APK not found: {apk_path}")

        start_time = time.time()
        self._log("install_apk_start", {"path": str(apk_path), "size_mb": apk_path.stat().st_size / 1024 / 1024})

        args = ["install"]
        if reinstall:
            args.append("-r")
        args.append(str(apk_path))

        for attempt in range(self.max_retries):
            code, stdout, stderr = self._adb(*args, timeout=300)
            output = stdout + stderr

            if code == 0 and "Success" in output:
                duration = time.time() - start_time
                self._log("install_apk_success", {"path": str(apk_path), "attempt": attempt + 1})
                return InstallStatus(
                    result=InstallResult.SUCCESS,
                    method=InstallMethod.DIRECT,
                    duration_seconds=duration,
                )

            if "INSTALL_FAILED_ALREADY_EXISTS" in output:
                return InstallStatus(InstallResult.ALREADY_INSTALLED, method=InstallMethod.DIRECT)

            # Retry with backoff
            delay = self._calculate_retry_delay(attempt)
            self._log("install_apk_retry", {"attempt": attempt + 1, "delay": delay, "error": output.strip()[:200]})
            time.sleep(delay)

        return InstallStatus(
            InstallResult.FAILED,
            method=InstallMethod.DIRECT,
            error=f"Failed after {self.max_retries} attempts: {stderr[:200]}",
            duration_seconds=time.time() - start_time,
        )

    def install_split_apks(self, apk_paths: list[Path | str], reinstall: bool = False) -> InstallStatus:
        """Install split APKs (App Bundle).

        Args:
            apk_paths: List of APK file paths (base + splits)
            reinstall: Allow reinstall

        Returns:
            Installation status
        """
        paths = [Path(p) for p in apk_paths]
        for p in paths:
            if not p.exists():
                return InstallStatus(InstallResult.FAILED, error=f"APK not found: {p}")

        start_time = time.time()
        total_size = sum(p.stat().st_size for p in paths) / 1024 / 1024
        self._log("install_split_start", {"count": len(paths), "total_size_mb": total_size})

        args = ["install-multiple"]
        if reinstall:
            args.append("-r")
        args.extend(str(p) for p in paths)

        for attempt in range(self.max_retries):
            code, stdout, stderr = self._adb(*args, timeout=600)
            output = stdout + stderr

            if code == 0 and "Success" in output:
                duration = time.time() - start_time
                self._log("install_split_success", {"count": len(paths), "attempt": attempt + 1})
                return InstallStatus(
                    result=InstallResult.SUCCESS,
                    method=InstallMethod.SPLIT,
                    duration_seconds=duration,
                )

            delay = self._calculate_retry_delay(attempt)
            self._log("install_split_retry", {"attempt": attempt + 1, "delay": delay})
            time.sleep(delay)

        return InstallStatus(
            InstallResult.FAILED,
            method=InstallMethod.SPLIT,
            error=f"Failed after {self.max_retries} attempts",
            duration_seconds=time.time() - start_time,
        )

    def download_apk(
        self,
        url: str,
        filename: str | None = None,
        expected_hash: str | None = None,
    ) -> Path | None:
        """Download APK from URL.

        Args:
            url: Download URL
            filename: Override filename
            expected_hash: Expected SHA256 hash for verification

        Returns:
            Path to downloaded file or None if failed
        """
        if not filename:
            parsed = urlparse(url)
            filename = Path(parsed.path).name or "download.apk"

        dest_path = self.download_dir / filename
        self._log("download_start", {"url": url[:100], "dest": str(dest_path)})

        try:
            with httpx.Client(follow_redirects=True, timeout=300) as client:
                with client.stream("GET", url) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get("content-length", 0))

                    with open(dest_path, "wb") as f:
                        downloaded = 0
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)

            # Verify hash if provided
            if expected_hash:
                actual_hash = self._calculate_hash(dest_path)
                if actual_hash.lower() != expected_hash.lower():
                    self._log(
                        "download_hash_mismatch",
                        {"expected": expected_hash[:16], "actual": actual_hash[:16]},
                        success=False,
                    )
                    dest_path.unlink()
                    return None

            self._log("download_success", {"path": str(dest_path), "size_mb": dest_path.stat().st_size / 1024 / 1024})
            return dest_path

        except Exception as e:
            self._log("download_failed", error=str(e), success=False)
            if dest_path.exists():
                dest_path.unlink()
            return None

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay before retry using gentle exponential backoff.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds

        Progression with 1.5x multiplier:
        0: 1s, 1: 1.5s, 2: 2.3s, 3: 3.4s, 4: 5s, 5: 7.6s,
        6: 11s, 7: 17s, 8: 26s, 9: 38s, 10: 58s (~1m),
        11: 87s, 12: 130s (~2m), 13: 195s (~3m), 14: 292s (~5m),
        15: 438s (~7m), 16+: 600s (10m cap)
        """
        base_delay = 1.0
        multiplier = 1.5  # Gentle exponential growth
        max_delay = 600.0  # 10 minutes cap for serious recovery
        delay = min(base_delay * (multiplier ** attempt), max_delay)
        return delay

    def install_from_url(
        self,
        url: str,
        package: str | None = None,
        expected_hash: str | None = None,
        reinstall: bool = False,
    ) -> InstallStatus:
        """Download and install APK from URL.

        Args:
            url: APK download URL
            package: Package name (for logging)
            expected_hash: SHA256 hash for verification
            reinstall: Allow reinstall

        Returns:
            Installation status
        """
        self._log("install_from_url_start", {"url": url[:100], "package": package})

        apk_path = self.download_apk(url, expected_hash=expected_hash)
        if not apk_path:
            return InstallStatus(InstallResult.DOWNLOAD_FAILED, error="Download failed")

        result = self.install_apk(apk_path, reinstall=reinstall)

        # Clean up downloaded file
        if apk_path.exists():
            apk_path.unlink()

        return result

    def get_apk_info(self, apk_path: Path | str) -> dict | None:
        """Extract info from APK using aapt.

        Args:
            apk_path: Path to APK file

        Returns:
            Dict with package, version, etc. or None if failed
        """
        apk_path = Path(apk_path)
        if not apk_path.exists():
            return None

        try:
            result = subprocess.run(
                ["aapt", "dump", "badging", str(apk_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return None

            info = {}
            output = result.stdout

            # Parse package name and version
            pkg_match = re.search(r"package: name='([^']+)' versionCode='([^']+)' versionName='([^']+)'", output)
            if pkg_match:
                info["package"] = pkg_match.group(1)
                info["version_code"] = pkg_match.group(2)
                info["version_name"] = pkg_match.group(3)

            # Parse label
            label_match = re.search(r"application-label:'([^']+)'", output)
            if label_match:
                info["label"] = label_match.group(1)

            return info

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def cleanup_downloads(self) -> int:
        """Clean up downloaded APK files.

        Returns:
            Number of files deleted
        """
        count = 0
        for f in self.download_dir.glob("*.apk"):
            f.unlink()
            count += 1
        self._log("cleanup", {"deleted": count})
        return count
