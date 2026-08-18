"""Detect exact and near-duplicate gloss frame sequences.

Gloss sample JSON files are expected to hold distinct signing sequences.
This module provides a deterministic SHA-256 fingerprint for exact clone
detection plus a time-aligned mean-landmark-distance scan for perceptual
near-duplicates.  A CI/CD helper (``assert_no_duplicates``) fails the build
when duplicate frame sequences are found across gloss files.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


class DuplicateFramesError(ValueError):
    """Raised when duplicate frame sequences are found across gloss files."""


def _is_valid_frame(frame: object) -> bool:
    """A valid frame is a list of landmarks, each landmark a list of scalars."""
    if not isinstance(frame, list) or len(frame) == 0:
        return False
    for landmark in frame:
        if (
            not isinstance(landmark, list)
            or len(landmark) == 0
            or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in landmark)
        ):
            return False
    return True


def read_frames(path: Path) -> list[np.ndarray]:
    """Load the landmarks of every frame as a flattened numeric vector.

    Frames that are not landmark lists of numeric values (for example the
    string placeholder ``"f"`` seen in the wild) are dropped so a corrupt row
    never masks a genuine duplicate.  Per-frame lengths are kept so ragged
    samples hash deterministically.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    frames = payload.get("frames") or []
    return [np.asarray(frame, dtype=np.float64).reshape(-1) for frame in frames if _is_valid_frame(frame)]


def sequence_fingerprint(frames: list[np.ndarray]) -> str:
    """Deterministic SHA-256 of a frame sequence.

    Every row is prefixed with its own flat length before the values, so two
    sequences hash equal only when their frame values are literally identical.
    """
    if not frames:
        return hashlib.sha256(b"").hexdigest()
    max_width = max(frame.shape[0] for frame in frames)
    dense = np.zeros((len(frames), max_width + 1), dtype=np.float64)
    for i, frame in enumerate(frames):
        width = int(frame.shape[0])
        dense[i, 0] = float(width)
        dense[i, 1 : 1 + width] = frame
    return hashlib.sha256(dense.tobytes()).hexdigest()


def _to_matrix(frames: list[np.ndarray]) -> np.ndarray:
    if not frames:
        return np.zeros((0, 0))
    width = max(frame.shape[0] for frame in frames)
    rows = np.zeros((len(frames), width), dtype=np.float64)
    for i, frame in enumerate(frames):
        rows[i, : frame.shape[0]] = frame
    return rows


def _aligned_frames(frames: np.ndarray, count: int) -> np.ndarray:
    indices = np.linspace(0, frames.shape[0] - 1, num=int(count)).round().astype(int)
    return frames[indices]


def _near_distance(a: list[np.ndarray], b: list[np.ndarray]) -> float | None:
    """Distance between two frame sequences after frame-count alignment."""
    if not a or not b:
        return None
    matrix_a = _to_matrix(a)
    matrix_b = _to_matrix(b)
    width = min(matrix_a.shape[1], matrix_b.shape[1])
    compared = min(matrix_a.shape[0], matrix_b.shape[0])
    aligned_a = _aligned_frames(matrix_a, compared)[:, :width]
    aligned_b = _aligned_frames(matrix_b, compared)[:, :width]
    frame_distances = np.sqrt(np.mean(np.square(aligned_a - aligned_b), axis=1))
    return float(np.mean(frame_distances))


def find_exact_groups(files: list[Path]) -> list[dict]:
    """Group files whose frame sequences hash identically.

    Files without at least one valid numeric landmark frame are skipped: an
    empty sequence cannot meaningfully "share" frames, and descriptor-only
    samples (for example the ``bounty-*.json`` annotations) use a different
    schema that is out of scope for frame-level detection.
    """
    buckets: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        frames = read_frames(path)
        if not frames:
            continue
        buckets[sequence_fingerprint(frames)].append(path)
    groups = []
    for digest, group in buckets.items():
        if len(group) > 1:
            groups.append(
                {
                    "sha256": digest,
                    "files": [str(path) for path in sorted(group, key=lambda p: str(p))],
                }
            )
    return sorted(groups, key=lambda g: g["files"][0])


def _counts_are_plausible(a_count: int, b_count: int, ratio: float) -> bool:
    larger = max(a_count, b_count)
    return larger == 0 or abs(a_count - b_count) <= max(1, int(ratio * larger))


def find_near_pairs(files: list[Path], eps: float = 1e-3, frame_ratio: float = 0.2) -> list[dict]:
    """Find pairs of files with near-identical frame sequences.

    Frame counts must be within ``frame_ratio`` of each other and the mean
    landmark distance must stay under ``eps`` after frame-count alignment.
    """
    entries = [
        {"frames": read_frames(path), "path": path, "digest": None} for path in files
    ]
    for entry in entries:
        entry["digest"] = sequence_fingerprint(entry["frames"])
    exact_indexes = {
        frozenset((i, j))
        for i in range(len(entries))
        for j in range(i + 1, len(entries))
        if entries[i]["digest"] == entries[j]["digest"]
    }
    pairs = []
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            if frozenset((i, j)) in exact_indexes:
                continue
            a, b = entries[i], entries[j]
            a_count, b_count = len(a["frames"]), len(b["frames"])
            if not _counts_are_plausible(a_count, b_count, frame_ratio):
                continue
            distance = _near_distance(a["frames"], b["frames"])
            if distance is not None and distance < eps:
                pairs.append(
                    {
                        "a": str(a["path"]),
                        "b": str(b["path"]),
                        "mean_landmark_distance": round(distance, 8),
                        "frames_a": a_count,
                        "frames_b": b_count,
                    }
                )
    return sorted(pairs, key=lambda p: (p["a"], p["b"]))


def scan_duplicates(directory: Path, eps: float = 1e-3, frame_ratio: float = 0.2) -> dict:
    """Scan a samples directory and report exact and near-duplicate sequences."""
    files = sorted(directory.glob("*.json"))
    exact_groups = find_exact_groups(files)
    near_pairs = find_near_pairs(files, eps=eps, frame_ratio=frame_ratio)
    return {
        "directory": str(directory),
        "files_scanned": len(files),
        "exact_clone_groups": exact_groups,
        "near_clone_pairs": near_pairs,
        "duplicate_count": len(exact_groups) + len(near_pairs),
    }


def assert_no_duplicates(directory: Path, eps: float = 1e-3) -> dict:
    """Fail when two gloss files share exact or near-identical frames.

    Intended for pytest and CI: a clean scan returns the report, a dirty scan
    raises :class:`DuplicateFramesError`.
    """
    report = scan_duplicates(directory, eps=eps)
    if report["duplicate_count"]:
        raise DuplicateFramesError(
            f"found {report['duplicate_count']} duplicate frame sequence(s) in {directory}: "
            f"{len(report['exact_clone_groups'])} exact group(s), "
            f"{len(report['near_clone_pairs'])} near pair(s)"
        )
    return report