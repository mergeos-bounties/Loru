from __future__ import annotations

import json
from pathlib import Path

import pytest

from loru.data.duplicates import (
    DuplicateFramesError,
    assert_no_duplicates,
    find_exact_groups,
    find_near_pairs,
    read_frames,
    scan_duplicates,
    sequence_fingerprint,
)


def _write_sample(path: Path, gloss: str, frames: list) -> Path:
    path.write_text(json.dumps({"gloss": gloss, "frames": frames}), encoding="utf-8")
    return path


def _jitter(frames: list, amount: float) -> list:
    return [[[v + amount for v in landmark] for landmark in frame] for frame in frames]


HELLO_FRAMES: list = [[[0.0, 0.5], [1.0, 1.5]], [[2.0, 2.5], [3.0, 3.5]], [[4.0, 4.5], [5.0, 5.5]]]


def test_fingerprint_is_deterministic_across_gloss_labels(tmp_path: Path) -> None:
    a = _write_sample(tmp_path / "a.json", "hello", HELLO_FRAMES)
    b = _write_sample(tmp_path / "b.json", "different_label", HELLO_FRAMES)

    assert sequence_fingerprint(read_frames(a)) == sequence_fingerprint(read_frames(b))


def test_exact_clones_are_grouped_by_hash(tmp_path: Path) -> None:
    _write_sample(tmp_path / "a.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "b.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "c.json", "world", [[[9.0]]])

    groups = find_exact_groups(list(tmp_path.glob("*.json")))

    assert len(groups) == 1
    assert len(groups[0]["files"]) == 2


def test_near_clones_are_detected_with_jitter(tmp_path: Path) -> None:
    _write_sample(tmp_path / "base.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "clone.json", "hello", _jitter(HELLO_FRAMES, 1e-4))
    _write_sample(tmp_path / "other.json", "world", [[[9.0, 9.0]], [[8.0, 8.0]]])

    pairs = find_near_pairs(list(tmp_path.glob("*.json")), eps=1e-3)

    assert len(pairs) == 1
    assert pairs[0]["mean_landmark_distance"] < 1e-3


def test_distinct_sequences_are_not_flagged(tmp_path: Path) -> None:
    _write_sample(tmp_path / "a.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "b.json", "bye", [[[9.0, 9.0]], [[8.0, 8.0]], [[7.0, 7.0]]])

    assert find_exact_groups(list(tmp_path.glob("*.json"))) == []
    assert find_near_pairs(list(tmp_path.glob("*.json")), eps=1e-3) == []


def test_malformed_frames_are_skipped(tmp_path: Path) -> None:
    malformed = [[0.0, 0.5], "f"]
    _write_sample(tmp_path / "clean.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "dirty.json", "hello", [malformed, *HELLO_FRAMES])

    groups = find_exact_groups(list(tmp_path.glob("*.json")))

    assert len(groups) == 1
    assert len(groups[0]["files"]) == 2


def test_frame_count_filter_ignores_subsequences(tmp_path: Path) -> None:
    _write_sample(tmp_path / "full.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "subset.json", "hello", HELLO_FRAMES[:2])

    pairs = find_near_pairs(list(tmp_path.glob("*.json")), eps=1e-3)

    assert pairs == []


def test_scan_reports_structure(tmp_path: Path) -> None:
    _write_sample(tmp_path / "a.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "b.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "c.json", "world", [[[9.0, 9.0]]])

    report = scan_duplicates(tmp_path)

    assert report["files_scanned"] == 3
    assert report["duplicate_count"] == 1
    assert len(report["exact_clone_groups"]) == 1


def test_descriptor_only_frames_are_not_flagged(tmp_path: Path) -> None:
    descriptor = [{"id": 1, "description": "Start", "duration_ms": 200}]
    _write_sample(tmp_path / "a.json", "thanks", descriptor)
    _write_sample(tmp_path / "b.json", "no", descriptor)

    report = scan_duplicates(tmp_path)

    assert report["files_scanned"] == 2
    assert report["duplicate_count"] == 0


def test_assert_no_duplicates_passes_on_clean_dir(tmp_path: Path) -> None:
    _write_sample(tmp_path / "a.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "b.json", "bye", [[[9.0, 9.0]], [[8.0, 8.0]]])

    report = assert_no_duplicates(tmp_path)

    assert report["duplicate_count"] == 0


def test_assert_no_duplicates_raises_on_clones(tmp_path: Path) -> None:
    _write_sample(tmp_path / "a.json", "hello", HELLO_FRAMES)
    _write_sample(tmp_path / "b.json", "hello", _jitter(HELLO_FRAMES, 1e-4))

    with pytest.raises(DuplicateFramesError, match="duplicate frame sequence"):
        assert_no_duplicates(tmp_path)