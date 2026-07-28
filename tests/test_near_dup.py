"""Tests for the near-duplicate gloss frame detector.

These exercises validate both the core ``find_near_duplicates`` routine and
the ``data near-dup`` CLI, using synthetic clones to keep the dataset small
and deterministic.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from loru.cli import app
from loru.data.near_dup import DEFAULT_THRESHOLD, find_near_duplicates


runner = CliRunner()


def _write_sample(directory: Path, name: str, gloss: str, frames: list) -> Path:
    path = directory / name
    payload = {"gloss": gloss, "language": "demo-asl", "frames": frames}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _seq(frame_count: int, base: float = 0.0, step: float = 1.0) -> list:
    return [[[base + idx * step]] for idx in range(frame_count)]


class TestFindNearDuplicates:
    def test_identical_samples_are_detected_as_near_duplicate(self, tmp_path: Path) -> None:
        frames = _seq(5)
        _write_sample(tmp_path, "a.json", "hello", frames)
        _write_sample(tmp_path, "b.json", "hello", frames)

        pairs = find_near_duplicates(tmp_path)

        assert len(pairs) == 1
        pair = pairs[0]
        assert pair["near_duplicate"] is True
        assert pair["mean_landmark_distance"] == 0.0
        assert pair["a"]["gloss"] == "hello"
        assert pair["b"]["gloss"] == "hello"
        assert pair["compared_frames"] == 5

    def test_distinct_sequences_are_not_flagged(self, tmp_path: Path) -> None:
        _write_sample(tmp_path, "a.json", "hello", _seq(3, base=0.0))
        _write_sample(tmp_path, "b.json", "thanks", _seq(3, base=10.0))

        pairs = find_near_duplicates(tmp_path)

        assert len(pairs) == 0

    def test_exact_window_window_are_captured_in_same_bucket(self, tmp_path: Path) -> None:
        """Two 3-frame sequences with the same landmarks are detected."""
        frames = _seq(3, base=0.0)
        _write_sample(tmp_path, "a.json", "hello", frames)
        _write_sample(tmp_path, "b.json", "hello", frames)

        pairs = find_near_duplicates(tmp_path)

        assert len(pairs) == 1
        pair = pairs[0]
        assert pair["near_duplicate"] is True
        assert pair["compared_frames"] == 3

    def test_returns_empty_for_empty_directory(self, tmp_path: Path) -> None:
        tmp_path.mkdir(parents=True, exist_ok=True)
        assert find_near_duplicates(tmp_path) == []

    def test_report_json_is_written_when_out_is_provided(self, tmp_path: Path) -> None:
        frames = _seq(4)
        _write_sample(tmp_path, "x.json", "hi", frames)
        _write_sample(tmp_path, "y.json", "hi", frames)
        out = tmp_path / "near_dup_report.json"

        from loru.data.near_dup import write_report

        summary = write_report(directory=tmp_path, out=out)

        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["near_duplicate_pairs"] == 1
        assert summary["near_duplicate_pairs"] == 1


class TestNearDupCLI:
    def test_cli_reports_near_duplicate_pairs(self, tmp_path: Path) -> None:
        frames = _seq(4)
        _write_sample(tmp_path, "hello.json", "hello", frames)
        _write_sample(tmp_path, "hello_copy.json", "hello", frames)

        result = runner.invoke(app, ["data", "near-dup", "--directory", str(tmp_path)])

        assert result.exit_code == 0
        assert "1 near-duplicate" in result.stdout
        assert "0.0" in result.stdout

    def test_cli_reports_none_when_no_duplicates(self, tmp_path: Path) -> None:
        _write_sample(tmp_path, "a.json", "hello", _seq(3, base=0.0))
        _write_sample(tmp_path, "b.json", "thanks", _seq(3, base=5.0))

        result = runner.invoke(app, ["data", "near-dup", "--directory", str(tmp_path)])

        assert result.exit_code == 0
        assert "No near-duplicate" in result.stdout

    def test_cli_can_write_json_report(self, tmp_path: Path) -> None:
        frames = _seq(3)
        _write_sample(tmp_path, "a.json", "ok", frames)
        _write_sample(tmp_path, "b.json", "ok", frames)
        out = tmp_path / "report.json"

        result = runner.invoke(
            app,
            ["data", "near-dup", "--directory", str(tmp_path), "--out", str(out)],
        )

        assert result.exit_code == 0
        assert out.exists()
        assert json.loads(out.read_text(encoding="utf-8"))["near_duplicate_pairs"] == 1

    def test_cli_accepts_custom_threshold(self, tmp_path: Path) -> None:
        # two nearly-identical sequences with tiny drift
        _write_sample(tmp_path, "a.json", "g", _seq(2, base=0.0))
        _write_sample(tmp_path, "b.json", "g", _seq(2, base=0.5))

        # default threshold excludes them
        loose = runner.invoke(app, ["data", "near-dup", "--directory", str(tmp_path), "--threshold", "1.0"])
        strict = runner.invoke(app, ["data", "near-dup", "--directory", str(tmp_path)])

        assert loose.exit_code == 0
        assert strict.exit_code == 0
        assert "near-duplicate" in loose.stdout
        assert "No near-duplicate" in strict.stdout
