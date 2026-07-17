from __future__ import annotations

from pathlib import Path

import numpy as np

from loru.data.loader import load_sequence


def _aligned_frames(frames: np.ndarray, count: int) -> np.ndarray:
    indices = np.linspace(0, frames.shape[0] - 1, num=count).round().astype(int)
    return frames[indices].reshape(count, -1)


def compare_gloss_samples(sample_a: Path, sample_b: Path) -> dict:
    """Return a deterministic frame and landmark-distance summary for two samples."""
    gloss_a, frames_a = load_sequence(sample_a)
    gloss_b, frames_b = load_sequence(sample_b)
    if frames_a.size == 0 or frames_b.size == 0:
        raise ValueError("both samples must contain at least one frame")

    feature_dim_a = frames_a[0].size
    feature_dim_b = frames_b[0].size
    if feature_dim_a != feature_dim_b:
        raise ValueError(
            f"samples have incompatible feature dimensions: {feature_dim_a} and {feature_dim_b}"
        )

    compared_frames = min(frames_a.shape[0], frames_b.shape[0])
    aligned_a = _aligned_frames(frames_a, compared_frames)
    aligned_b = _aligned_frames(frames_b, compared_frames)
    frame_distances = np.sqrt(np.mean(np.square(aligned_a - aligned_b), axis=1))
    mean_distance = float(np.mean(frame_distances))
    max_distance = float(np.max(frame_distances))

    return {
        "a": {"path": str(sample_a), "gloss": gloss_a, "frames": int(frames_a.shape[0])},
        "b": {"path": str(sample_b), "gloss": gloss_b, "frames": int(frames_b.shape[0])},
        "frame_delta": abs(int(frames_a.shape[0]) - int(frames_b.shape[0])),
        "compared_frames": compared_frames,
        "mean_landmark_distance": round(mean_distance, 6),
        "max_landmark_distance": round(max_distance, 6),
        "possible_clone": gloss_a == gloss_b and mean_distance < 0.001,
    }
