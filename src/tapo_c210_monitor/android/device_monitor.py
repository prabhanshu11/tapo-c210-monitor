"""Device monitoring and auto-recovery for Android emulators."""

import subprocess
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

from .session import Session


class DeviceState(Enum):
    """Device connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    OFFLINE = "offline"
    RECOVERING = "recovering"


@dataclass
class EmulatorConfig:
    """Configuration for Android emulator."""
    avd_name: str
    sdk_path: Path
    gpu_mode: str = "auto"  # Use KVM hardware acceleration when available
    memory_mb: int = 2048
    no_snapshot: bool = True
    no_audio: bool = True
    no_boot_anim: bool = True
    extra_args: list[str] | None = None


class DeviceMonitor:
    """Monitors device connection and handles auto-recovery."""

    def __init__(
        self,
        emulator_config: EmulatorConfig | None = None,
        check_interval: float = 5.0,
        max_recovery_attempts: int = 3,
        session: Session | None = None,
    ):
        """Initialize device monitor.

        Args:
            emulator_config: Emulator configuration for auto-restart
            check_interval: Seconds between health checks
            max_recovery_attempts: Max consecutive recovery attempts
            session: Session for logging events
        """
        self.emulator_config = emulator_config
        self.check_interval = check_interval
        self.max_recovery_attempts = max_recovery_attempts
        self.session = session

        self.state = DeviceState.DISCONNECTED
        self.device_serial: str | None = None
        self.emulator_pid: int | None = None
        self.recovery_attempts = 0

        self._monitor_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._state_callbacks: list[Callable[[DeviceState, DeviceState], None]] = []

    def _log(self, event_type: str, data: dict | None = None, success: bool = True, error: str | None = None) -> None:
        """Log event to session if available."""
        if self.session:
            self.session.log_emulator_event(event_type, data, success, error)
        print(f"[DeviceMonitor] {event_type}: {data or ''} {'ERROR: ' + error if error else ''}")

    def _run_adb(self, *args: str, timeout: int = 30) -> tuple[int, str, str]:
        """Run ADB command with timeout.

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = ["adb"] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except FileNotFoundError:
            return -1, "", "ADB not found"

    def _set_state(self, new_state: DeviceState) -> None:
        """Update state and notify callbacks."""
        if new_state != self.state:
            old_state = self.state
            self.state = new_state
            self._log("state_change", {"from": old_state.value, "to": new_state.value})
            for callback in self._state_callbacks:
                try:
                    callback(old_state, new_state)
                except Exception as e:
                    self._log("callback_error", {"error": str(e)}, success=False)

    def add_state_callback(self, callback: Callable[[DeviceState, DeviceState], None]) -> None:
        """Add callback for state changes.

        Args:
            callback: Function(old_state, new_state) to call on state change
        """
        self._state_callbacks.append(callback)

    def check_device_connected(self) -> bool:
        """Check if device is connected and responsive.

        Returns:
            True if device is connected and responding
        """
        code, stdout, stderr = self._run_adb("devices", timeout=10)
        if code != 0:
            return False

        lines = stdout.strip().split("\n")[1:]  # Skip header
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                self.device_serial = parts[0]
                return True

        return False

    def check_device_responsive(self) -> bool:
        """Check if connected device responds to commands.

        Returns:
            True if device responds
        """
        if not self.device_serial:
            return False

        code, stdout, _ = self._run_adb(
            "-s", self.device_serial,
            "shell", "getprop", "sys.boot_completed",
            timeout=10,
        )
        return code == 0 and stdout.strip() == "1"

    def wait_for_device(self, timeout: int = 120) -> bool:
        """Wait for device to become available.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if device connected within timeout
        """
        self._set_state(DeviceState.CONNECTING)
        self._log("wait_for_device", {"timeout": timeout})

        start = time.time()
        while time.time() - start < timeout:
            if self.check_device_connected():
                # Wait for boot completion
                boot_start = time.time()
                while time.time() - boot_start < 60:
                    if self.check_device_responsive():
                        self._set_state(DeviceState.CONNECTED)
                        self._log("device_ready", {"serial": self.device_serial})
                        return True
                    time.sleep(2)
            time.sleep(2)

        self._set_state(DeviceState.DISCONNECTED)
        self._log("wait_timeout", {"timeout": timeout}, success=False)
        return False

    def start_emulator(self) -> bool:
        """Start the Android emulator.

        Returns:
            True if emulator started successfully
        """
        if not self.emulator_config:
            self._log("start_emulator_failed", error="No emulator config")
            return False

        config = self.emulator_config
        emulator_path = config.sdk_path / "emulator" / "emulator"

        if not emulator_path.exists():
            self._log("start_emulator_failed", error=f"Emulator not found at {emulator_path}")
            return False

        # Build command
        cmd = [
            str(emulator_path),
            "-avd", config.avd_name,
            "-memory", str(config.memory_mb),
            "-gpu", config.gpu_mode,
        ]

        if config.no_snapshot:
            cmd.append("-no-snapshot")
        if config.no_audio:
            cmd.append("-no-audio")
        if config.no_boot_anim:
            cmd.append("-no-boot-anim")
        if config.extra_args:
            cmd.extend(config.extra_args)

        self._log("start_emulator", {"command": " ".join(cmd)})

        try:
            # Start emulator in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            self.emulator_pid = process.pid
            self._log("emulator_started", {"pid": self.emulator_pid})

            # Wait for device
            return self.wait_for_device()

        except Exception as e:
            self._log("start_emulator_failed", error=str(e), success=False)
            return False

    def stop_emulator(self) -> None:
        """Stop the Android emulator."""
        if self.device_serial:
            self._run_adb("-s", self.device_serial, "emu", "kill", timeout=10)

        if self.emulator_pid:
            try:
                subprocess.run(["kill", str(self.emulator_pid)], timeout=5)
            except Exception:
                pass
            self.emulator_pid = None

        self._set_state(DeviceState.DISCONNECTED)
        self._log("emulator_stopped")

    def recover(self) -> bool:
        """Attempt to recover device connection.

        Returns:
            True if recovery successful
        """
        self.recovery_attempts += 1
        if self.recovery_attempts > self.max_recovery_attempts:
            self._log(
                "recovery_failed",
                {"attempts": self.recovery_attempts},
                success=False,
                error="Max recovery attempts exceeded",
            )
            return False

        self._set_state(DeviceState.RECOVERING)
        self._log("recovery_start", {"attempt": self.recovery_attempts})

        # Try reconnecting ADB first
        self._run_adb("kill-server", timeout=10)
        time.sleep(2)
        self._run_adb("start-server", timeout=10)
        time.sleep(2)

        if self.check_device_connected() and self.check_device_responsive():
            self._set_state(DeviceState.CONNECTED)
            self.recovery_attempts = 0
            self._log("recovery_success", {"method": "adb_restart"})
            return True

        # Try restarting emulator
        if self.emulator_config:
            self.stop_emulator()
            time.sleep(3)
            if self.start_emulator():
                self.recovery_attempts = 0
                self._log("recovery_success", {"method": "emulator_restart"})
                return True

        self._set_state(DeviceState.DISCONNECTED)
        self._log("recovery_failed", {"attempt": self.recovery_attempts}, success=False)
        return False

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while not self._stop_event.is_set():
            if self.state == DeviceState.CONNECTED:
                # Check if still connected
                if not self.check_device_connected():
                    self._set_state(DeviceState.OFFLINE)
                    self._log("device_disconnected", success=False, error="Device went offline")
                elif not self.check_device_responsive():
                    self._set_state(DeviceState.OFFLINE)
                    self._log("device_unresponsive", success=False, error="Device not responding")

            elif self.state in (DeviceState.OFFLINE, DeviceState.DISCONNECTED):
                # Try to recover
                self.recover()

            self._stop_event.wait(self.check_interval)

    def start_monitoring(self) -> None:
        """Start background monitoring thread."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self._log("monitoring_started")

    def stop_monitoring(self) -> None:
        """Stop background monitoring thread."""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=10)
        self._log("monitoring_stopped")

    def ensure_connected(self, timeout: int = 120) -> bool:
        """Ensure device is connected, starting emulator if needed.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if device is connected
        """
        if self.check_device_connected() and self.check_device_responsive():
            self._set_state(DeviceState.CONNECTED)
            return True

        if self.emulator_config:
            return self.start_emulator()

        return self.wait_for_device(timeout)
