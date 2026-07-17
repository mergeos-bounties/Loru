from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from loru.cli import app
from loru.data.compare import compare_gloss_samples


def _write_sample(path: Path, gloss: str, frames: list) -> Path:
    path.write_text(json.dumps({"gloss": gloss, "frames": frames}), encoding="utf-8")
    return path


def test_identical_samples_are_flagged_as_possible_clone(tmp_path: Path) -> None:
    frames = [[[0.0, 0.0]], [[1.0, 1.0]]]
    a = _write_sample(tmp_path / "a.json", "hello", frames)
    b = _write_sample(tmp_path / "b.json", "hello", frames)

    result = compare_gloss_samples(a, b)

    assert result["frame_delta"] == 0
    assert result["mean_landmark_distance"] == 0.0
    assert result["possible_clone"] is True


def test_different_frame_counts_are_time_aligned(tmp_path: Path) -> None:
    a = _write_sample(tmp_path / "a.json", "hello", [[[0.0]], [[1.0]], [[2.0]]])
    b = _write_sample(tmp_path / "b.json", "hello", [[[0.0]], [[3.0]]])

    result = compare_gloss_samples(a, b)

    assert result["frame_delta"] == 1
    assert result["compared_frames"] == 2
    assert result["mean_landmark_distance"] == 0.5
    assert result["max_landmark_distance"] == 1.0


def test_incompatible_landmarks_are_rejected(tmp_path: Path) -> None:
    a = _write_sample(tmp_path / "a.json", "hello", [[[0.0, 1.0]]])
    b = _write_sample(tmp_path / "b.json", "hello", [[[0.0, 1.0, 2.0]]])

    with pytest.raises(ValueError, match="incompatible feature dimensions"):
        compare_gloss_samples(a, b)


def test_compare_cli_prints_summary(tmp_path: Path) -> None:
    a = _write_sample(tmp_path / "a.json", "hello", [[[0.0]], [[1.0]]])
    b = _write_sample(tmp_path / "b.json", "hello", [[[0.0]], [[1.0]]])

    result = CliRunner().invoke(app, ["gloss", "compare", "--a", str(a), "--b", str(b)])

    assert result.exit_code == 0
    assert '"mean_landmark_distance": 0.0' in result.stdout
    assert '"possible_clone": true' in result.stdout
