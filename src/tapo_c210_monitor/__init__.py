"""TAPO C210 Monitor - Intelligent camera monitoring system."""

__version__ = "0.1.0"

# Lazy imports to avoid dependency issues at startup
def __getattr__(name):
    if name == "TapoCamera":
        from .camera import TapoCamera
        return TapoCamera
    elif name == "StreamCapture":
        from .stream import StreamCapture
        return StreamCapture
    elif name == "RecordingSync":
        from .sync import RecordingSync
        return RecordingSync
    elif name == "LLMVision":
        from .vision import LLMVision
        return LLMVision
    elif name == "IntelligentScreen":
        from .android import IntelligentScreen
        return IntelligentScreen
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "TapoCamera",
    "StreamCapture",
    "RecordingSync",
    "LLMVision",
    "IntelligentScreen",
]
