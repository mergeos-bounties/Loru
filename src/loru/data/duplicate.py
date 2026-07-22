from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from loru.data.compare import compare_gloss_samples


@dataclass
class NearDuplicateReport:
    file_a: Path
    file_b: Path
    gloss: str
    mean_distance: float
    max_distance: float
    frame_delta: int
    is_near_duplicate: bool

    def as_dict(self) -> dict:
        return {
            "file_a": str(self.file_a),
            "file_b": str(self.file_b),
            "gloss": self.gloss,
            "mean_distance": self.mean_distance,
            "max_distance": self.max_distance,
            "frame_delta": self.frame_delta,
            "is_near_duplicate": self.is_near_duplicate,
        }


# Threshold: if mean landmark distance is below this, flag as near-duplicate
# This is deliberately strict — near-identical synthetic frames should be < 0.001
DISTANCE_THRESHOLD = 0.001


def find_near_duplicates(
    samples_dir: Path,
    distance_threshold: float = DISTANCE_THRESHOLD,
) -> list[NearDuplicateReport]:
    """Scan a directory of gloss JSON files and report near-duplicate pairs.

    Two samples are considered near-duplicates if:
    - They share the same gloss name, AND
    - Their mean frame landmark distance is below the threshold

    Returns a list of NearDuplicateReport, one per flagged pair.
    Skips comparison of a file against itself.
    """
    from loru.data.loader import list_sample_files

    files = list_sample_files(samples_dir)
    reports: list[NearDuplicateReport] = []

    # Compare every pair once (i < j)
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            path_a = files[i]
            path_b = files[j]
            try:
                result = compare_gloss_samples(path_a, path_b)
            except (ValueError, KeyError):
                # Incompatible dimensions or malformed JSON — skip
                continue

            mean_dist = result["mean_landmark_distance"]
            gloss = result["a"]["gloss"]

            # Only flag same-gloss pairs as near-duplicates
            same_gloss = gloss == result["b"]["gloss"]
            is_near = same_gloss and mean_dist < distance_threshold

            if is_near:
                reports.append(
                    NearDuplicateReport(
                        file_a=path_a,
                        file_b=path_b,
                        gloss=gloss,
                        mean_distance=mean_dist,
                        max_distance=result["max_landmark_distance"],
                        frame_delta=result["frame_delta"],
                        is_near_duplicate=True,
                    )
                )

    return reports


def has_near_duplicates(
    samples_dir: Path,
    distance_threshold: float = DISTANCE_THRESHOLD,
) -> bool:
    """Return True if any near-duplicate pair is found (for use in pytest)."""
    return len(find_near_duplicates(samples_dir, distance_threshold)) > 0