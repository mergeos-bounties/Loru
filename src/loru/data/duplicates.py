from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

import numpy as np

from loru.data.loader import load_sequence


def frame_hashes(frames: np.ndarray, decimals: int = 3) -> list[str]:
    """Return stable per-frame hashes after rounding landmark coordinates."""
    if frames.ndim < 2 or frames.shape[0] == 0:
        return []
    rounded = np.round(frames.reshape(frames.shape[0], -1), decimals=decimals)
    hashes = []
    for row in rounded:
        digest = hashlib.sha256(row.tobytes()).hexdigest()
        hashes.append(digest[:16])
    return hashes


def best_offset_match(
    left: list[str],
    right: list[str],
    *,
    max_offset: int = 4,
    min_overlap: int = 4,
) -> dict:
    """Find the best shifted frame-hash match between two sequences."""
    best = {"offset": 0, "overlap": 0, "matches": 0, "score": 0.0}
    if not left or not right:
        return best

    for offset in range(-max_offset, max_offset + 1):
        if offset >= 0:
            left_start = offset
            right_start = 0
        else:
            left_start = 0
            right_start = -offset
        overlap = min(len(left) - left_start, len(right) - right_start)
        if overlap < min_overlap:
            continue
        matches = sum(
            1
            for i in range(overlap)
            if left[left_start + i] == right[right_start + i]
        )
        score = matches / overlap
        if (score, matches, overlap) > (best["score"], best["matches"], best["overlap"]):
            best = {
                "offset": offset,
                "overlap": overlap,
                "matches": matches,
                "score": score,
            }
    return best


def find_near_duplicate_glosses(
    files: Iterable[Path],
    *,
    threshold: float = 0.9,
    max_offset: int = 4,
    min_overlap: int = 4,
    decimals: int = 3,
) -> list[dict]:
    """Report pairs whose rounded frame sequences are near-identical."""
    loaded = []
    for path in sorted(Path(p) for p in files):
        gloss, frames = load_sequence(path)
        loaded.append(
            {
                "path": path,
                "gloss": gloss,
                "hashes": frame_hashes(frames, decimals=decimals),
                "frames": int(frames.shape[0]) if frames.ndim >= 1 else 0,
            }
        )

    matches = []
    for i, left in enumerate(loaded):
        for right in loaded[i + 1 :]:
            result = best_offset_match(
                left["hashes"],
                right["hashes"],
                max_offset=max_offset,
                min_overlap=min_overlap,
            )
            if result["score"] >= threshold:
                matches.append(
                    {
                        "left": str(left["path"]),
                        "right": str(right["path"]),
                        "left_gloss": left["gloss"],
                        "right_gloss": right["gloss"],
                        "left_frames": left["frames"],
                        "right_frames": right["frames"],
                        "offset": result["offset"],
                        "overlap": result["overlap"],
                        "matching_frames": result["matches"],
                        "score": round(result["score"], 4),
                    }
                )
    return sorted(matches, key=lambda m: (-m["score"], m["left"], m["right"]))


def assert_no_near_duplicate_glosses(
    files: Iterable[Path],
    *,
    threshold: float = 0.9,
    max_offset: int = 4,
    min_overlap: int = 4,
    decimals: int = 3,
) -> None:
    matches = find_near_duplicate_glosses(
        files,
        threshold=threshold,
        max_offset=max_offset,
        min_overlap=min_overlap,
        decimals=decimals,
    )
    if not matches:
        return
    details = ", ".join(
        f"{Path(m['left']).name}<->{Path(m['right']).name} score={m['score']} offset={m['offset']}"
        for m in matches[:5]
    )
    raise AssertionError(f"near-duplicate gloss frames detected: {details}")
