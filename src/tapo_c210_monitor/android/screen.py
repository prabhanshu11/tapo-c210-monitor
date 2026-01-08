"""Screen capture and analysis for Android automation."""

import io
import tempfile
from pathlib import Path
from typing import Callable
import numpy as np
from PIL import Image

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class ScreenCapture:
    """Capture and analyze Android screen content."""

    def __init__(self, controller: "AndroidController"):
        """Initialize screen capture.

        Args:
            controller: AndroidController instance
        """
        self.controller = controller
        self._screen_size: tuple[int, int] | None = None

    @property
    def screen_size(self) -> tuple[int, int]:
        """Get cached screen size."""
        if self._screen_size is None:
            self._screen_size = self.controller.get_screen_size()
        return self._screen_size

    def capture(self) -> Image.Image:
        """Capture current screen as PIL Image.

        Returns:
            PIL Image of screen
        """
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            temp_path = Path(f.name)

        try:
            self.controller.screenshot(temp_path)
            return Image.open(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def capture_numpy(self) -> np.ndarray:
        """Capture screen as numpy array (for OpenCV).

        Returns:
            numpy array in BGR format
        """
        import cv2
        img = self.capture()
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def capture_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> Image.Image:
        """Capture specific region of screen.

        Args:
            x, y: Top-left corner
            width, height: Region dimensions

        Returns:
            Cropped PIL Image
        """
        full_screen = self.capture()
        return full_screen.crop((x, y, x + width, y + height))

    def find_text(self, target_text: str) -> list[dict]:
        """Find text on screen using OCR.

        Args:
            target_text: Text to find (case-insensitive)

        Returns:
            List of matches with coordinates
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract not available")

        img = self.capture()
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        matches = []
        target_lower = target_text.lower()

        for i, text in enumerate(data["text"]):
            if text and target_lower in text.lower():
                x = data["left"][i]
                y = data["top"][i]
                w = data["width"][i]
                h = data["height"][i]
                matches.append({
                    "text": text,
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                    "center_x": x + w // 2,
                    "center_y": y + h // 2,
                    "confidence": data["conf"][i],
                })

        return matches

    def get_all_text(self) -> str:
        """Extract all text from screen.

        Returns:
            All visible text
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract not available")

        img = self.capture()
        return pytesseract.image_to_string(img)

    def get_text_boxes(self, min_confidence: int = 60) -> list[dict]:
        """Get all text boxes with coordinates.

        Args:
            min_confidence: Minimum OCR confidence (0-100)

        Returns:
            List of text box dictionaries
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract not available")

        img = self.capture()
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        boxes = []
        for i, text in enumerate(data["text"]):
            if text.strip() and data["conf"][i] >= min_confidence:
                boxes.append({
                    "text": text,
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                    "confidence": data["conf"][i],
                })

        return boxes

    def tap_text(self, target_text: str) -> bool:
        """Find and tap on text.

        Args:
            target_text: Text to find and tap

        Returns:
            True if text found and tapped
        """
        matches = self.find_text(target_text)
        if not matches:
            print(f"Text not found: {target_text}")
            return False

        # Tap on first (highest) match
        best = max(matches, key=lambda m: m["confidence"])
        self.controller.tap(best["center_x"], best["center_y"])
        return True

    def wait_for_text(
        self,
        target_text: str,
        timeout_seconds: float = 10.0,
        poll_interval: float = 0.5,
    ) -> bool:
        """Wait for text to appear on screen.

        Args:
            target_text: Text to wait for
            timeout_seconds: Maximum wait time
            poll_interval: Time between checks

        Returns:
            True if text found within timeout
        """
        import time
        start = time.time()

        while time.time() - start < timeout_seconds:
            if self.find_text(target_text):
                return True
            time.sleep(poll_interval)

        return False

    def find_image(
        self,
        template_path: str | Path,
        threshold: float = 0.8,
    ) -> list[dict]:
        """Find image template on screen using template matching.

        Args:
            template_path: Path to template image
            threshold: Match threshold (0-1)

        Returns:
            List of match locations
        """
        import cv2

        screen = self.capture_numpy()
        template = cv2.imread(str(template_path))

        if template is None:
            raise ValueError(f"Could not load template: {template_path}")

        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        h, w = template.shape[:2]
        matches = []

        for pt in zip(*locations[::-1]):
            matches.append({
                "x": pt[0],
                "y": pt[1],
                "width": w,
                "height": h,
                "center_x": pt[0] + w // 2,
                "center_y": pt[1] + h // 2,
                "confidence": result[pt[1], pt[0]],
            })

        return matches

    def tap_image(
        self,
        template_path: str | Path,
        threshold: float = 0.8,
    ) -> bool:
        """Find and tap on image template.

        Args:
            template_path: Path to template image
            threshold: Match threshold

        Returns:
            True if template found and tapped
        """
        matches = self.find_image(template_path, threshold)
        if not matches:
            print(f"Image not found: {template_path}")
            return False

        best = max(matches, key=lambda m: m["confidence"])
        self.controller.tap(best["center_x"], best["center_y"])
        return True

    def wait_for_image(
        self,
        template_path: str | Path,
        timeout_seconds: float = 10.0,
        poll_interval: float = 0.5,
        threshold: float = 0.8,
    ) -> bool:
        """Wait for image template to appear.

        Args:
            template_path: Path to template image
            timeout_seconds: Maximum wait time
            poll_interval: Time between checks
            threshold: Match threshold

        Returns:
            True if template found within timeout
        """
        import time
        start = time.time()

        while time.time() - start < timeout_seconds:
            if self.find_image(template_path, threshold):
                return True
            time.sleep(poll_interval)

        return False

    def compare_screens(
        self,
        img1: Image.Image,
        img2: Image.Image,
    ) -> float:
        """Compare two screen images.

        Args:
            img1, img2: Images to compare

        Returns:
            Similarity score (0-1, higher = more similar)
        """
        import cv2

        # Convert to numpy
        arr1 = np.array(img1.convert("L"))
        arr2 = np.array(img2.convert("L"))

        # Ensure same size
        if arr1.shape != arr2.shape:
            arr2 = cv2.resize(arr2, (arr1.shape[1], arr1.shape[0]))

        # Calculate structural similarity
        diff = cv2.absdiff(arr1, arr2)
        similarity = 1.0 - (np.mean(diff) / 255.0)

        return similarity

    def wait_for_screen_change(
        self,
        threshold: float = 0.95,
        timeout_seconds: float = 10.0,
        poll_interval: float = 0.3,
    ) -> bool:
        """Wait for screen to change.

        Args:
            threshold: Similarity threshold (screen changed if below)
            timeout_seconds: Maximum wait time
            poll_interval: Time between checks

        Returns:
            True if screen changed within timeout
        """
        import time

        initial = self.capture()
        start = time.time()

        while time.time() - start < timeout_seconds:
            time.sleep(poll_interval)
            current = self.capture()
            similarity = self.compare_screens(initial, current)

            if similarity < threshold:
                return True

        return False

    def save_screenshot(self, path: str | Path) -> Path:
        """Save current screen to file.

        Args:
            path: Output file path

        Returns:
            Path to saved file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        img = self.capture()
        img.save(path)
        return path
