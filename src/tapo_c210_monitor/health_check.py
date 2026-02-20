"""Camera health checks including mount failure detection."""

import hashlib
from pathlib import Path
from typing import List, Tuple
from PIL import Image
import imagehash


class CameraHealthCheck:
    """Detect camera physical issues like mount failures."""
    
    @staticmethod
    def compute_image_hash(image_path: Path) -> str:
        """Compute perceptual hash of image."""
        img = Image.open(image_path)
        return str(imagehash.phash(img))
    
    @staticmethod
    def compare_hashes(hash1: str, hash2: str) -> float:
        """Compare two image hashes, return similarity 0-1."""
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        # Hamming distance - lower is more similar
        # Max distance is 64 for phash
        distance = h1 - h2
        similarity = 1 - (distance / 64.0)
        return similarity
    
    @classmethod
    def detect_mount_failure(
        cls,
        frames: List[Path],
        similarity_threshold: float = 0.85
    ) -> Tuple[bool, str]:
        """
        Detect if camera is physically stuck/fallen.
        
        Args:
            frames: List of captured frame paths from different positions
            similarity_threshold: If avg similarity > this, likely stuck
            
        Returns:
            (is_stuck, reason)
        """
        if len(frames) < 3:
            return False, "Not enough frames to compare"
        
        # Compute hashes for all frames
        hashes = []
        for frame in frames:
            if frame.exists():
                hashes.append((frame.name, cls.compute_image_hash(frame)))
        
        if len(hashes) < 3:
            return False, "Not enough valid frames"
        
        # Compare all pairs
        similarities = []
        for i in range(len(hashes)):
            for j in range(i + 1, len(hashes)):
                sim = cls.compare_hashes(hashes[i][1], hashes[j][1])
                similarities.append(sim)
        
        avg_similarity = sum(similarities) / len(similarities)
        
        if avg_similarity > similarity_threshold:
            return True, (
                f"MOUNT FAILURE DETECTED: All {len(frames)} frames show same scene "
                f"(avg similarity: {avg_similarity:.1%}). "
                f"Camera may have fallen or tape lost grip. "
                f"Physical inspection required."
            )
        
        return False, f"Frames varied normally (avg similarity: {avg_similarity:.1%})"
    
    @staticmethod
    def check_tilt_anomaly(tilt_value: float) -> Tuple[bool, str]:
        """Check if tilt angle indicates camera fell."""
        # Extreme downward tilt often indicates camera fell
        if tilt_value < -0.9:
            return True, f"Extreme downward tilt ({tilt_value:.2f}) - camera may have fallen"
        if tilt_value > 0.95:
            return True, f"Extreme upward tilt ({tilt_value:.2f}) - unusual position"
        return False, "Tilt angle normal"
