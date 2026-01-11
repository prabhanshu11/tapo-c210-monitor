"""Change Detection + LLM Vision Analysis.

Monitors the ring buffer for scene changes and uses multimodal LLM
to describe what changed.
"""

import os
import time
import json
import base64
import httpx
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Tuple
from PIL import Image
import io


@dataclass
class ChangeEvent:
    """Detected change event."""
    timestamp: float
    change_score: float
    frames_before: List[str]  # Paths to frames before change
    frames_after: List[str]   # Paths to frames after change
    llm_analysis: Optional[str] = None


class ChangeDetector:
    """Detects scene changes from ring buffer frames."""

    def __init__(
        self,
        ringbuffer_url: str = "http://localhost:8085",
        change_threshold: float = 0.15,
        check_interval: float = 2.0,
    ):
        self.ringbuffer_url = ringbuffer_url
        self.change_threshold = change_threshold
        self.check_interval = check_interval
        self.last_frame_hash: Optional[np.ndarray] = None
        self.running = False

    def _get_frames(self, seconds_ago: List[float], output_dir: str) -> List[str]:
        """Get frames from ring buffer."""
        params = {
            "seconds_ago": ",".join(str(s) for s in seconds_ago),
            "output_dir": output_dir,
        }
        resp = httpx.get(f"{self.ringbuffer_url}/frames", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json().get("frames", [])

    def _compute_frame_hash(self, frame_path: str) -> np.ndarray:
        """Compute perceptual hash of frame for comparison."""
        img = Image.open(frame_path).convert("L")  # Grayscale
        img = img.resize((32, 32), Image.Resampling.LANCZOS)
        arr = np.array(img, dtype=np.float32)
        return arr / 255.0

    def _compare_frames(self, hash1: np.ndarray, hash2: np.ndarray) -> float:
        """Compare two frame hashes. Returns change score 0-1."""
        diff = np.abs(hash1 - hash2)
        return float(np.mean(diff))

    def check_for_change(self, output_dir: str = "/tmp/change_detect") -> Optional[ChangeEvent]:
        """Check current frame against last frame for changes."""
        os.makedirs(output_dir, exist_ok=True)

        # Get current frame
        frames = self._get_frames([0], output_dir)
        if not frames:
            return None

        current_hash = self._compute_frame_hash(frames[0])

        if self.last_frame_hash is None:
            self.last_frame_hash = current_hash
            return None

        # Compare with previous
        change_score = self._compare_frames(self.last_frame_hash, current_hash)

        if change_score > self.change_threshold:
            # Change detected! Get before and after frames
            # Before: 5s and 3s ago (before the change)
            # After: 0s and 2s ahead (we'll wait for these)

            frames_before = self._get_frames([5, 3], output_dir)

            # Wait a bit for "after" frames
            time.sleep(2)
            frames_after = self._get_frames([0, 2], output_dir)

            event = ChangeEvent(
                timestamp=time.time(),
                change_score=change_score,
                frames_before=frames_before,
                frames_after=frames_after,
            )

            self.last_frame_hash = current_hash
            return event

        self.last_frame_hash = current_hash
        return None


class LLMVisionAnalyzer:
    """Analyzes change events using multimodal LLM."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-thinking-exp",
    ):
        # Try to get API key from environment
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable required")

    def _encode_image(self, path: str) -> str:
        """Encode image to base64."""
        with open(path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    def _get_mime_type(self, path: str) -> str:
        """Get MIME type from file extension."""
        ext = Path(path).suffix.lower()
        return {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }.get(ext, "image/jpeg")

    def analyze_change(self, event: ChangeEvent) -> str:
        """Analyze a change event using Gemini."""

        # Build the prompt with images
        parts = []

        # Add before frames
        parts.append({"text": "BEFORE the change (frames from a few seconds earlier):\n"})
        for i, frame_path in enumerate(event.frames_before):
            if os.path.exists(frame_path):
                parts.append({
                    "inline_data": {
                        "mime_type": self._get_mime_type(frame_path),
                        "data": self._encode_image(frame_path),
                    }
                })
                parts.append({"text": f"Before frame {i+1}\n"})

        # Add after frames
        parts.append({"text": "\nAFTER the change (frames from the moment of change and after):\n"})
        for i, frame_path in enumerate(event.frames_after):
            if os.path.exists(frame_path):
                parts.append({
                    "inline_data": {
                        "mime_type": self._get_mime_type(frame_path),
                        "data": self._encode_image(frame_path),
                    }
                })
                parts.append({"text": f"After frame {i+1}\n"})

        # Add the question
        parts.append({
            "text": """
Looking at the BEFORE and AFTER frames from this security camera:

1. Do you see a change between before and after? (YES/NO)
2. If YES, what kind of change is it? Describe specifically:
   - What appeared or disappeared?
   - What moved?
   - Any people, objects, or animals involved?
   - Is this a significant security event or just normal activity?

Be concise but specific.
"""
        })

        # Call Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 500,
            }
        }

        resp = httpx.post(
            url,
            params={"key": self.api_key},
            json=payload,
            timeout=60,
        )

        if resp.status_code != 200:
            return f"LLM API error: {resp.status_code} - {resp.text}"

        result = resp.json()

        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            return f"Failed to parse response: {e}\n{json.dumps(result, indent=2)}"


class ChangeMonitor:
    """Continuous monitoring for changes with LLM analysis."""

    def __init__(
        self,
        ringbuffer_url: str = "http://localhost:8085",
        change_threshold: float = 0.15,
        check_interval: float = 2.0,
        output_dir: str = "/tmp/change_monitor",
    ):
        self.detector = ChangeDetector(
            ringbuffer_url=ringbuffer_url,
            change_threshold=change_threshold,
            check_interval=check_interval,
        )
        self.analyzer: Optional[LLMVisionAnalyzer] = None
        self.output_dir = output_dir
        self.events: List[ChangeEvent] = []
        self.running = False

        # Try to initialize analyzer
        try:
            self.analyzer = LLMVisionAnalyzer()
        except ValueError as e:
            print(f"Warning: LLM analyzer not available: {e}")

    def start(self, callback=None):
        """Start monitoring. Callback is called for each change event."""
        self.running = True
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"Starting change monitor (threshold: {self.detector.change_threshold})")
        print(f"Output directory: {self.output_dir}")
        print(f"LLM analyzer: {'enabled' if self.analyzer else 'disabled'}")

        while self.running:
            try:
                event = self.detector.check_for_change(self.output_dir)

                if event:
                    print(f"\n[{time.strftime('%H:%M:%S')}] CHANGE DETECTED! Score: {event.change_score:.3f}")

                    # Run LLM analysis if available
                    if self.analyzer:
                        print("Analyzing with LLM...")
                        event.llm_analysis = self.analyzer.analyze_change(event)
                        print(f"Analysis:\n{event.llm_analysis}")

                    self.events.append(event)

                    if callback:
                        callback(event)

            except Exception as e:
                print(f"Error checking for changes: {e}")

            time.sleep(self.detector.check_interval)

    def stop(self):
        """Stop monitoring."""
        self.running = False


def main():
    """Run change monitor."""
    import argparse

    parser = argparse.ArgumentParser(description="Change Detection Monitor")
    parser.add_argument("--ringbuffer-url", default="http://localhost:8085")
    parser.add_argument("--threshold", type=float, default=0.15)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--output-dir", default="/tmp/change_monitor")
    args = parser.parse_args()

    monitor = ChangeMonitor(
        ringbuffer_url=args.ringbuffer_url,
        change_threshold=args.threshold,
        check_interval=args.interval,
        output_dir=args.output_dir,
    )

    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        monitor.stop()


if __name__ == "__main__":
    main()
