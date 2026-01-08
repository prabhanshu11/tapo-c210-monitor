"""Intelligent screen capture with LLM vision for UI element detection."""

import time
from pathlib import Path
from PIL import Image

from .controller import AndroidController
from .screen import ScreenCapture
from ..vision import LLMVision, UIElement, VisionResult


class IntelligentScreen:
    """Android screen with LLM-powered UI element detection.

    Combines traditional screen capture with LLM vision for intelligent
    element detection that doesn't require templates or OCR.
    """

    def __init__(
        self,
        controller: AndroidController,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
    ):
        """Initialize intelligent screen.

        Args:
            controller: AndroidController instance
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            model: LLM model for vision (gpt-4o-mini, gpt-4o, claude-sonnet, gemini-flash)
        """
        self.controller = controller
        self.screen = ScreenCapture(controller)
        self.vision = LLMVision(api_key=api_key, model=model)
        self._last_analysis: VisionResult | None = None

    def capture(self) -> Image.Image:
        """Capture current screen."""
        return self.screen.capture()

    def analyze(self, task: str = "Identify all interactive UI elements") -> VisionResult:
        """Analyze current screen with LLM vision.

        Args:
            task: Specific task or question about the UI

        Returns:
            VisionResult with detected elements
        """
        img = self.capture()
        self._last_analysis = self.vision.analyze_screen(img, task)
        return self._last_analysis

    def find_element(self, target: str) -> UIElement | None:
        """Find a specific UI element by description.

        Args:
            target: Description of element to find (e.g., "settings button")

        Returns:
            UIElement if found, None otherwise
        """
        img = self.capture()
        return self.vision.find_element(img, target)

    def tap_element(self, target: str) -> bool:
        """Find and tap a UI element.

        Args:
            target: Description of element to tap

        Returns:
            True if element found and tapped
        """
        element = self.find_element(target)
        if element:
            self.controller.tap(element.center_x, element.center_y)
            return True
        return False

    def wait_for_element(
        self,
        target: str,
        timeout_seconds: float = 10.0,
        poll_interval: float = 1.0,
    ) -> UIElement | None:
        """Wait for a UI element to appear.

        Args:
            target: Description of element to wait for
            timeout_seconds: Maximum wait time
            poll_interval: Time between checks

        Returns:
            UIElement if found within timeout, None otherwise
        """
        start = time.time()
        while time.time() - start < timeout_seconds:
            element = self.find_element(target)
            if element:
                return element
            time.sleep(poll_interval)
        return None

    def tap_and_wait(
        self,
        target: str,
        wait_for: str | None = None,
        timeout: float = 5.0,
    ) -> bool:
        """Tap element and optionally wait for another element.

        Args:
            target: Element to tap
            wait_for: Element to wait for after tap (optional)
            timeout: Wait timeout in seconds

        Returns:
            True if tap successful (and wait element found if specified)
        """
        if not self.tap_element(target):
            return False

        if wait_for:
            return self.wait_for_element(wait_for, timeout) is not None

        # Wait for screen change
        time.sleep(0.5)
        return True

    def get_screen_description(self) -> str:
        """Get LLM description of current screen.

        Returns:
            Natural language description of what's on screen
        """
        result = self.analyze("Describe what screen this is and its main purpose")
        return result.screen_description

    def is_on_screen(self, screen_description: str) -> bool:
        """Check if we're on a specific screen.

        Args:
            screen_description: Description to match against

        Returns:
            True if current screen matches description
        """
        img = self.capture()
        element = self.vision.find_element(img, f"screen matching: {screen_description}")
        return element is not None and element.confidence > 0.7

    def save_screenshot(self, path: str | Path) -> Path:
        """Save current screen to file."""
        return self.screen.save_screenshot(path)

    def close(self):
        """Clean up resources."""
        self.vision.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
