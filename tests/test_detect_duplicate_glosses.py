"""Tests for near-duplicate gloss frame detector."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.detect_duplicate_glosses import (
    _frame_distance,
    _sequence_distance,
    _min_offset_distance,
    find_near_duplicates,
)


def test_frame_distance_identical() -> None:
    """Identical landmark vectors have zero distance."""
    a = [1.0, 2.0, 3.0]
    b = [1.0, 2.0, 3.0]
    assert _frame_distance(a, b) == 0.0


def test_frame_distance_different() -> None:
    """Different vectors have positive distance."""
    a = [0.0, 0.0, 0.0]
    b = [1.0, 1.0, 1.0]
    assert _frame_distance(a, b) > 0.0


def test_frame_distance_empty() -> None:
    """Empty vectors return inf distance."""
    assert _frame_distance([], []) == float("inf")
    assert _frame_distance([1.0], []) == float("inf")


def test_sequence_distance_identical() -> None:
    """Identical sequences have zero distance."""
    seq = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    assert _sequence_distance(seq, seq) == 0.0


def test_sequence_distance_different() -> None:
    """Different sequences have positive distance."""
    a = [[0.0, 0.0], [0.0, 0.0]]
    b = [[1.0, 1.0], [1.0, 1.0]]
    assert _sequence_distance(a, b) > 0.0


def test_min_offset_distance_no_offset() -> None:
    """Identical sequences found at offset 0."""
    seq = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    dist, offset = _min_offset_distance(seq, seq, max_offset=3)
    assert dist == 0.0
    assert offset == 0


def test_min_offset_distance_shifted() -> None:
    """Shifted identical subsequence found at correct offset.

    seq_a = [a, b, c, d], seq_b = [x, y, a, b, c]
    a,b,c overlap when offset=-2 (seq_b shifted right by 2).
    """
    seq_a = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]]
    seq_b = [[9.0, 9.0], [9.0, 9.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    dist, offset = _min_offset_distance(seq_a, seq_b, max_offset=5)
    assert dist < 0.01
    assert offset == -2


def test_find_near_duplicates_no_samples(tmp_path: Path) -> None:
    """Empty directory returns empty list."""
    empty = tmp_path / "empty"
    empty.mkdir()
    assert find_near_duplicates(samples_dir=empty) == []


def test_find_near_duplicates_none(tmp_path: Path) -> None:
    """No duplicates when all glosses are unique."""
    files = [
        {"gloss": "hello", "frames": [[1.0, 0.0], [0.0, 1.0]]},
        {"gloss": "world", "frames": [[9.0, 9.0], [8.0, 8.0], [7.0, 7.0]]},
    ]
    for f in files:
        (tmp_path / f"{f['gloss']}.json").write_text(
            json.dumps(f), encoding="utf-8"
        )
    result = find_near_duplicates(threshold=0.05, samples_dir=tmp_path)
    assert result == []


def test_find_near_duplicates_found(tmp_path: Path) -> None:
    """Near-duplicate glosses are detected."""
    identical_frames = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    files = [
        {"gloss": "hello", "frames": identical_frames},
        {"gloss": "hi", "frames": identical_frames},
        {"gloss": "world", "frames": [[9.0, 9.0], [8.0, 8.0]]},
    ]
    for f in files:
        (tmp_path / f"{f['gloss']}.json").write_text(
            json.dumps(f), encoding="utf-8"
        )
    result = find_near_duplicates(threshold=0.05, samples_dir=tmp_path)
    assert len(result) >= 1
    pair = result[0]
    assert pair["gloss_a"] in ("hello", "hi")
    assert pair["gloss_b"] in ("hello", "hi")
    assert pair["distance"] < 0.01


def test_find_near_duplicates_synthetic_clones(tmp_path: Path) -> None:
    """Synthetic clones with slight noise are detected at appropriate threshold."""
    base_frames = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.5, 0.5]]
    noisy_frames = [
        [1.01, 0.0], [0.0, 0.99], [1.0, 1.02], [0.5, 0.51]
    ]  # ~1% noise
    files = [
        {"gloss": "original", "frames": base_frames},
        {"gloss": "clone_noisy", "frames": noisy_frames},
        {"gloss": "different", "frames": [[9.0, 9.0], [8.0, 8.0]]},
    ]
    for f in files:
        (tmp_path / f"{f['gloss']}.json").write_text(
            json.dumps(f), encoding="utf-8"
        )
    # Use a threshold that catches the noisy clone
    result = find_near_duplicates(threshold=0.1, samples_dir=tmp_path)
    assert len(result) >= 1
    pair = result[0]
    assert "original" in (pair["gloss_a"], pair["gloss_b"])
    assert "clone_noisy" in (pair["gloss_a"], pair["gloss_b"])