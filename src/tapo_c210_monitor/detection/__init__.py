"""Object detection modules for continuous scene monitoring."""

from .yolo_detector import YOLODetector, Detection
from .object_logger import ObjectLogger
from .scene_scanner import ActiveSceneManager, SceneScanner
from .frame_store import FrameStore

__all__ = [
    "YOLODetector", "Detection", "ObjectLogger",
    "ActiveSceneManager", "SceneScanner",  # SceneScanner = backward-compat alias
    "FrameStore",
]
