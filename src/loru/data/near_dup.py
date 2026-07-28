"""Batch detector of near-duplicate gloss frame sequences.

Scans a directory of Loru landmark-sample JSON files and reports pairs of
samples that share near-identical frame sequences. Detects both exact clones
(same frame count and identical landmarks) and offset copies (one sequence
is a shifted window of another) by comparing sequences whose frame counts
differ by one.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from loru.data.loader import load_sequence, list_sample_files

DEFAULT_THRESHOLD = 1e-6


def _load_frames(path: Path) -> tuple[str, np.ndarray]:
    """Load frames, returning an empty array when a sample has none."""
    gloss, frames = load_sequence(path)
    if frames.ndim < 2 or frames.shape[0] == 0:
        return gloss, np.empty((0, 1), dtype=np.float64)
    return gloss, frames


def _pair_distance(a: np.ndarray, b: np.ndarray) -> tuple[int, float, float]:
    """Time-align two sequences and return (common_frames, mean_dist, max_dist).

    Mirrors :func:`loru.data.compare.compare_gloss_samples` so the detector
    agrees with the pair-comparison CLI.
    """
    n = min(a.shape[0], b.shape[0])
    if n == 0:
        raise ValueError("at least one common frame is required")
    a_idx = np.linspace(0, a.shape[0] - 1, num=n).round().astype(int)
    b_idx = np.linspace(0, b.shape[0] - 1, num=n).round().astype(int)
    aligned_a = a[a_idx].reshape(n, -1)
    aligned_b = b[b_idx].reshape(n, -1)
    diffs = aligned_a - aligned_b
    frame_distances = np.sqrt(np.mean(np.square(diffs), axis=1))
    return int(n), float(np.mean(frame_distances)), float(np.max(frame_distances))


def _make_result(
    a: Path,
    b: Path,
    mean_dist: float,
    max_dist: float,
    compared: int,
    gloss_a: str,
    gloss_b: str,
    threshold: float,
) -> dict[str, Any]:
    return {
        "a": {"path": str(a), "gloss": gloss_a},
        "b": {"path": str(b), "gloss": gloss_b},
        "compared_frames": int(compared),
        "mean_landmark_distance": round(mean_dist, 6),
        "max_landmark_distance": round(max_dist, 6),
        "near_duplicate": bool(mean_dist <= threshold),
    }


def find_near_duplicates(
    directory: Path | None = None,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[dict[str, Any]]:
    """Return pairs of near-duplicate samples inside *directory*.

    Strategy (fast bucket filter + exact distance verification):

    1. Bucket every sample by (frame_count, feature_dim). Near-identical
       sequences with the same shape live in the same bucket, so the pairwise
       scan touches only likely candidates.
    2. Within each bucket, run an exact time-aligned landmark distance.
    3. Additionally compare neighbours whose frame counts differ by one,
       catching offset clones where one sequence is a shifted window of
       another.
    """
    files = list_sample_files(directory)
    if not files:
        return []

    buckets: dict[tuple[int, int], list[Path]] = defaultdict(list)
    by_frame_count: dict[int, list[Path]] = defaultdict(list)
    for path in files:
        _gloss, frames = _load_frames(path)
        fc = int(frames.shape[0]) if frames.ndim >= 2 else 0
        fd = int(frames.shape[1]) if frames.ndim >= 2 and frames.shape[1] else 1
        buckets[(fc, fd)].append(path)
        by_frame_count[fc].append(path)

    results: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def _maybe_add(
        a: Path,
        b: Path,
        mean_dist: float,
        max_dist: float,
        compared: int,
        gloss_a: str,
        gloss_b: str,
    ) -> None:
        key = (str(a), str(b))
        if key in seen or (str(b), str(a)) in seen:
            return
        seen.add(key)
        results.append(_make_result(a, b, mean_dist, max_dist, compared, gloss_a, gloss_b, threshold))

    for _bucket_key, paths in buckets.items():
        for i in range(len(paths)):
            gloss_a, frames_a = _load_frames(paths[i])
            for j in range(i + 1, len(paths)):
                gloss_b, frames_b = _load_frames(paths[j])
                try:
                    compared, mean_dist, max_dist = _pair_distance(frames_a, frames_b)
                except ValueError:
                    continue
                if mean_dist <= threshold:
                    _maybe_add(paths[i], paths[j], mean_dist, max_dist, compared, gloss_a, gloss_b)

    frame_counts = sorted(set(fc for fc, _fd in buckets))
    for i, fc in enumerate(frame_counts):
        if i + 1 < len(frame_counts) and frame_counts[i + 1] - fc == 1:
            neighbours = by_frame_count[fc] + by_frame_count[frame_counts[i + 1]]
            by_fd: dict[int, list[Path]] = defaultdict(list)
            for path in neighbours:
                _, frames = _load_frames(path)
                fd = int(frames.shape[1]) if frames.ndim >= 2 and frames.shape[1] else 1
                by_fd[fd].append(path)
            for _fd, paths in by_fd.items():
                for ii in range(len(paths)):
                    gloss_a, frames_a = _load_frames(paths[ii])
                    for jj in range(ii + 1, len(paths)):
                        gloss_b, frames_b = _load_frames(paths[jj])
                        try:
                            compared, mean_dist, max_dist = _pair_distance(frames_a, frames_b)
                        except ValueError:
                            continue
                        if mean_dist <= threshold:
                            _maybe_add(paths[ii], paths[jj], mean_dist, max_dist, compared, gloss_a, gloss_b)

    return results


def write_report(
    directory: Path | None = None,
    out: Path | None = None,
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    """Scan *directory* and return the detection summary, writing a JSON file
    to *out* when provided.
    """
    results = find_near_duplicates(directory, threshold=threshold)
    summary = {"near_duplicate_pairs": len(results), "threshold": threshold, "pairs": results}
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
