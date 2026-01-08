"""Android automation modules for controlling Tapo app via ADB."""

from .controller import AndroidController
from .screen import ScreenCapture
from .ui import UIAutomation
from .file_transfer import FileTransfer
from .intelligent_screen import IntelligentScreen
from .tapo_automator import TapoAutomator, TapoCredentials, CameraConfig
from .session import Session, SessionManager, SessionEvent
from .device_monitor import DeviceMonitor, DeviceState, EmulatorConfig
from .app_installer import AppInstaller, InstallMethod, InstallResult, InstallStatus

__all__ = [
    "AndroidController",
    "ScreenCapture",
    "UIAutomation",
    "FileTransfer",
    "IntelligentScreen",
    "TapoAutomator",
    "TapoCredentials",
    "CameraConfig",
    "Session",
    "SessionManager",
    "SessionEvent",
    "DeviceMonitor",
    "DeviceState",
    "EmulatorConfig",
    "AppInstaller",
    "InstallMethod",
    "InstallResult",
    "InstallStatus",
]
