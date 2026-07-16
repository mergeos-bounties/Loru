from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from loru.data.duplicates import (
    assert_no_near_duplicate_glosses,
    best_offset_match,
    find_near_duplicate_glosses,
    frame_hashes,
)


def write_sequence(path: Path, gloss: str, frames: list) -> Path:
    path.write_text(
        json.dumps({"gloss": gloss, "fps": 15, "frames": frames}),
        encoding="utf-8",
    )
    return path


def make_frames(start: float, count: int = 8) -> list:
    frames = []
    for i in range(count):
        base = start + i * 0.01
        frames.append(
            [
                [base, base + 0.1, base + 0.2],
                [base + 0.3, base + 0.4, base + 0.5],
            ]
        )
    return frames


def test_frame_hashes_are_stable_after_rounding() -> None:
    frames = make_frames(0.1, count=2)
    hashes = frame_hashes(np.asarray(frames), decimals=3)
    nudged = frame_hashes(np.asarray(frames) + 0.0001, decimals=3)
    assert hashes == nudged
    assert len(set(hashes)) == 2


def test_best_offset_match_finds_shifted_clone() -> None:
    left = ["a", "b", "c", "d", "e"]
    right = ["x", "b", "c", "d", "e"]
    result = best_offset_match(left, right, max_offset=2, min_overlap=3)
    assert result["offset"] == 0
    assert result["matches"] == 4
    assert result["score"] == 0.8


def test_find_near_duplicate_glosses_reports_synthetic_clone(tmp_path: Path) -> None:
    original = make_frames(0.1, count=8)
    clone_with_offset = make_frames(9.0, count=1) + original
    unrelated = make_frames(1.5, count=8)

    a = write_sequence(tmp_path / "hello.json", "hello", original)
    b = write_sequence(tmp_path / "hello_clone.json", "hello_clone", clone_with_offset)
    c = write_sequence(tmp_path / "thanks.json", "thanks", unrelated)

    matches = find_near_duplicate_glosses([a, b, c], threshold=0.9, max_offset=2)

    assert len(matches) == 1
    assert matches[0]["left"].endswith("hello.json")
    assert matches[0]["right"].endswith("hello_clone.json")
    assert matches[0]["offset"] == 0 or matches[0]["offset"] == -1
    assert matches[0]["score"] >= 0.9


def test_assert_no_near_duplicate_glosses_fails_on_clone(tmp_path: Path) -> None:
    original = write_sequence(tmp_path / "a.json", "a", make_frames(0.2, count=6))
    clone = write_sequence(tmp_path / "b.json", "b", make_frames(0.2, count=6))

    with pytest.raises(AssertionError, match="near-duplicate gloss frames detected"):
        assert_no_near_duplicate_glosses([original, clone])


def test_assert_no_near_duplicate_glosses_allows_distinct_sequences(tmp_path: Path) -> None:
    a = write_sequence(tmp_path / "a.json", "a", make_frames(0.2, count=6))
    b = write_sequence(tmp_path / "b.json", "b", make_frames(2.2, count=6))

    assert_no_near_duplicate_glosses([a, b])
