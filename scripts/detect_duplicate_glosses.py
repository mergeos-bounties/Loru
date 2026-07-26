"""Detect near-duplicate gloss frame sequences across sign-pack files.

Compares all gloss files in data/samples/ — if two glosses share
near-identical frame sequences (above a similarity threshold), the
detector reports them as potential duplicates with their frame offset.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


def _load_gloss(path: Path) -> dict[str, Any]:
    """Load a gloss JSON file and return its metadata + frames."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": str(path),
        "gloss": raw.get("gloss", path.stem),
        "language": raw.get("language", "?"),
        "fps": raw.get("fps", 15),
        "frames": raw.get("frames", []),
    }


def _frame_distance(a: list[float], b: list[float]) -> float:
    """Euclidean distance between two landmark vectors (padded/truncated)."""
    n = min(len(a), len(b))
    if n == 0:
        return float("inf")
    # Zip matching elements
    pairs = list(zip(a[:n], b[:n]))
    return math.sqrt(sum((x - y) ** 2 for x, y in pairs)) / math.sqrt(n)


def _sequence_distance(
    seq_a: list[list[float]], seq_b: list[list[float]]
) -> float:
    """Average frame distance between two sequences of equal length."""
    n = min(len(seq_a), len(seq_b))
    if n == 0:
        return float("inf")
    total = 0.0
    for i in range(n):
        total += _frame_distance(seq_a[i], seq_b[i])
    return total / n


def _min_offset_distance(
    seq_a: list[list[float]],
    seq_b: list[list[float]],
    max_offset: int = 5,
) -> tuple[float, int]:
    """Find minimum average distance by sliding seq_b over seq_a.

    Returns (min_distance, offset) where offset > 0 means seq_b is
    shifted right relative to seq_a, and offset < 0 means left.
    """
    best_dist = float("inf")
    best_offset = 0
    for offset in range(-max_offset, max_offset + 1):
        if offset >= 0:
            a_slice = seq_a[offset:]
            b_slice = seq_b[: len(seq_a) - offset]
        else:
            a_slice = seq_a[: len(seq_b) + offset]
            b_slice = seq_b[-offset:]
        if len(a_slice) < 2 or len(b_slice) < 2:
            continue
        dist = _sequence_distance(a_slice, b_slice)
        if dist < best_dist:
            best_dist = dist
            best_offset = offset
    return best_dist, best_offset


def find_near_duplicates(
    threshold: float = 0.05,
    max_offset: int = 5,
    samples_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Scan all gloss files and find near-duplicate pairs.

    Args:
        threshold: Maximum average frame distance to consider as duplicate.
        max_offset: Max frame offset to check when aligning sequences.
        samples_dir: Directory containing gloss JSON files.

    Returns:
        List of duplicate reports, each with gloss_a, gloss_b, distance, offset.
    """
    samples_dir = samples_dir or SAMPLES_DIR
    if not samples_dir.is_dir():
        return []

    gloss_files = sorted(samples_dir.glob("*.json"))
    glosses = [_load_gloss(p) for p in gloss_files if p.is_file()]

    if not glosses:
        return []

    duplicates: list[dict[str, Any]] = []
    checked: set[tuple[str, str]] = set()

    for i in range(len(glosses)):
        for j in range(i + 1, len(glosses)):
            a = glosses[i]
            b = glosses[j]
            key = (a["gloss"], b["gloss"])
            if key in checked:
                continue
            checked.add(key)

            frames_a = a["frames"]
            frames_b = b["frames"]

            if not frames_a or not frames_b:
                continue

            dist, offset = _min_offset_distance(
                frames_a, frames_b, max_offset=max_offset
            )

            if dist <= threshold:
                duplicates.append(
                    {
                        "gloss_a": a["gloss"],
                        "path_a": a["path"],
                        "gloss_b": b["gloss"],
                        "path_b": b["path"],
                        "distance": round(dist, 6),
                        "offset_frames": offset,
                        "frames_a": len(frames_a),
                        "frames_b": len(frames_b),
                    }
                )

    return sorted(duplicates, key=lambda x: x["distance"])


def main() -> None:
    """CLI entry point: scan and report near-duplicate gloss frames."""
    threshold = 0.05
    if len(sys.argv) > 1:
        try:
            threshold = float(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [threshold]", file=sys.stderr)
            sys.exit(1)

    duplicates = find_near_duplicates(threshold=threshold)

    if not duplicates:
        print(f"No near-duplicate gloss frames found (threshold={threshold}).")
        sys.exit(0)

    print(f"Found {len(duplicates)} near-duplicate pair(s) (threshold={threshold}):")
    print()
    for d in duplicates:
        print(
            f"  {d['gloss_a']} ↔ {d['gloss_b']}: "
            f"distance={d['distance']} offset={d['offset_frames']}f "
            f"(len={d['frames_a']}/{d['frames_b']})"
        )
        print(f"    {d['path_a']}")
        print(f"    {d['path_b']}")
    sys.exit(1)  # Fail so CI catches duplicates


if __name__ == "__main__":
    main()