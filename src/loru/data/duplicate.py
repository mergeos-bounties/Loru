from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from loru.config import SAMPLES_DIR
from loru.data.loader import list_sample_files, load_sequence


@dataclass
class NearDuplicateReport:
    """Report for a pair of near-duplicate gloss files."""
    file_a: str
    file_b: str
    gloss: str
    frames_a: int
    frames_b: int
    mean_distance: float
    max_distance: float
    threshold: float


DISTANCE_THRESHOLD = 0.001


def _frame_hash(frames: np.ndarray) -> str:
    """Compute SHA256 hash of frame data."""
    return hashlib.sha256(frames.tobytes()).hexdigest()


def _mean_landmark_distance(frames_a: np.ndarray, frames_b: np.ndarray) -> tuple[float, float]:
    """Compute mean and max landmark distance between two frame sequences."""
    if frames_a.size == 0 or frames_b.size == 0:
        return float('inf'), float('inf')
    
    feature_dim_a = frames_a[0].size
    feature_dim_b = frames_b[0].size
    if feature_dim_a != feature_dim_b:
        return float('inf'), float('inf')
    
    compared_frames = min(frames_a.shape[0], frames_b.shape[0])
    if compared_frames == 0:
        return float('inf'), float('inf')
    
    # Align frames by temporal resampling
    indices_a = np.linspace(0, frames_a.shape[0] - 1, num=compared_frames).round().astype(int)
    indices_b = np.linspace(0, frames_b.shape[0] - 1, num=compared_frames).round().astype(int)
    
    aligned_a = frames_a[indices_a].reshape(compared_frames, -1)
    aligned_b = frames_b[indices_b].reshape(compared_frames, -1)
    
    frame_distances = np.sqrt(np.mean(np.square(aligned_a - aligned_b), axis=1))
    mean_distance = float(np.mean(frame_distances))
    max_distance = float(np.max(frame_distances))
    
    return mean_distance, max_distance


def find_near_duplicates(
    samples_dir: Path | str | None = None,
    threshold: float = DISTANCE_THRESHOLD
) -> list[NearDuplicateReport]:
    """
    Scan a samples directory for near-duplicate gloss frame sequences.
    
    Args:
        samples_dir: Directory containing gloss JSON files. Defaults to SAMPLES_DIR.
        threshold: Mean landmark distance threshold for near-duplicate detection.
        
    Returns:
        List of NearDuplicateReport for each near-duplicate pair found.
    """
    dir_path = Path(samples_dir) if samples_dir else SAMPLES_DIR
    files = list_sample_files(dir_path)
    
    # Group files by gloss
    gloss_to_files: dict[str, list[Path]] = {}
    for path in files:
        gloss, frames = load_sequence(path)
        if frames.size > 0:
            gloss_to_files.setdefault(gloss, []).append(path)
    
    reports = []
    for gloss, gloss_files in gloss_to_files.items():
        if len(gloss_files) < 2:
            continue
            
        # Load all sequences for this gloss
        sequences = []
        for path in gloss_files:
            _gloss_name, frames = load_sequence(path)
            sequences.append((path, frames))
        
        # Compare each pair
        for i in range(len(sequences)):
            for j in range(i + 1, len(sequences)):
                path_a, frames_a = sequences[i]
                path_b, frames_b = sequences[j]
                
                mean_dist, max_dist = _mean_landmark_distance(frames_a, frames_b)
                
                if mean_dist < threshold:
                    reports.append(NearDuplicateReport(
                        file_a=str(path_a),
                        file_b=str(path_b),
                        gloss=gloss,
                        frames_a=int(frames_a.shape[0]),
                        frames_b=int(frames_b.shape[0]),
                        mean_distance=round(mean_dist, 6),
                        max_distance=round(max_dist, 6),
                        threshold=threshold,
                    ))
    
    return reports


def has_near_duplicates(
    samples_dir: Path | str | None = None,
    threshold: float = DISTANCE_THRESHOLD
) -> bool:
    """
    Check if any near-duplicate gloss frame sequences exist.
    
    Args:
        samples_dir: Directory containing gloss JSON files. Defaults to SAMPLES_DIR.
        threshold: Mean landmark distance threshold for near-duplicate detection.
        
    Returns:
        True if any near-duplicate pair is found, False otherwise.
    """
    return len(find_near_duplicates(samples_dir, threshold)) > 0