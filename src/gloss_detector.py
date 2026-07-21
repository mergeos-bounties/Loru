import os
import hashlib
from typing import List, Dict, Tuple
from src.gloss_utils import load_gloss_file, compare_frame_sequences

class GlossFrameDetector:
    """
    Detects near-duplicate frame sequences across gloss files.
    """

    def __init__(self, similarity_threshold: float = 0.9):
        """
        Initialize the detector with a similarity threshold.

        Args:
            similarity_threshold: Minimum similarity score to consider frames as duplicates (0-1)
        """
        self.similarity_threshold = similarity_threshold

    def detect_clones(self, gloss_dir: str) -> Dict[str, List[Tuple[str, float]]]:
        """
        Detect near-duplicate frame sequences in gloss files within a directory.

        Args:
            gloss_dir: Path to directory containing gloss files

        Returns:
            Dictionary mapping file paths to lists of (matching_file, similarity_score) tuples
        """
        gloss_files = [f for f in os.listdir(gloss_dir) if f.endswith('.json')]
        file_hashes = {}
        clones = {}

        for file in gloss_files:
            file_path = os.path.join(gloss_dir, file)
            frames = load_gloss_file(file_path)
            frame_hash = self._generate_frame_hash(frames)

            for existing_file, existing_hash in file_hashes.items():
                similarity = compare_frame_sequences(frames, existing_hash)
                if similarity >= self.similarity_threshold:
                    if file_path not in clones:
                        clones[file_path] = []
                    clones[file_path].append((existing_file, similarity))

            file_hashes[file_path] = frames

        return clones

    def _generate_frame_hash(self, frames: List[Dict]) -> str:
        """
        Generate a hash for a frame sequence.

        Args:
            frames: List of frame dictionaries

        Returns:
            Hash string representing the frame sequence
        """
        frame_str = str(frames).encode('utf-8')
        return hashlib.sha256(frame_str).hexdigest()