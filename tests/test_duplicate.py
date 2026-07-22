from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from loru.cli import app
from loru.data.duplicate import (
    DISTANCE_THRESHOLD,
    NearDuplicateReport,
    find_near_duplicates,
    has_near_duplicates,
)


def _write_sample(path, gloss: str, frames: list) -> None:
    """Write a synthetic gloss sample JSON."""
    path.write_text(
        json.dumps({"gloss": gloss, "frames": frames}),
        encoding="utf-8",
    )


class TestNearDuplicateDetector:
    def test_no_duplicates_when_all_unique(self, tmp_path) -> None:
        """Different glosses should never be flagged."""
        _write_sample(tmp_path / "hello.json", "hello", [[[0.0]], [[1.0]]])
        _write_sample(tmp_path / "thanks.json", "thanks", [[[5.0]], [[6.0]]])

        reports = find_near_duplicates(tmp_path)
        assert reports == []
        assert has_near_duplicates(tmp_path) is False

    def test_identical_same_gloss_flagged(self, tmp_path) -> None:
        """Same gloss with identical frames must be flagged."""
        frames = [[[0.0, 0.0]], [[1.0, 1.0]], [[2.0, 2.0]]]
        _write_sample(tmp_path / "a.json", "hello", frames)
        _write_sample(tmp_path / "b.json", "hello", frames)

        reports = find_near_duplicates(tmp_path, distance_threshold=DISTANCE_THRESHOLD)
        assert len(reports) == 1
        dup = reports[0]
        assert dup.gloss == "hello"
        assert dup.mean_distance == 0.0
        assert dup.is_near_duplicate is True
        assert has_near_duplicates(tmp_path) is True

    def test_near_identical_frames_with_small_variance_not_flagged(self, tmp_path) -> None:
        """Same gloss with small but non-zero variance should NOT be flagged."""
        # Mean distance ~0.07 — above 0.001 threshold
        frames_a = [[[0.0, 0.0]], [[1.0, 1.0]]]
        frames_b = [[[0.1, 0.1]], [[1.1, 1.1]]]
        _write_sample(tmp_path / "a.json", "hello", frames_a)
        _write_sample(tmp_path / "b.json", "hello", frames_b)

        reports = find_near_duplicates(tmp_path, distance_threshold=DISTANCE_THRESHOLD)
        assert reports == []

    def test_different_gloss_same_frames_not_flagged(self, tmp_path) -> None:
        """Same frames but different gloss names should NOT be flagged."""
        frames = [[[0.0, 0.0]], [[1.0, 1.0]]]
        _write_sample(tmp_path / "a.json", "hello", frames)
        _write_sample(tmp_path / "b.json", "thanks", frames)

        reports = find_near_duplicates(tmp_path)
        assert reports == []

    def test_incompatible_dimensions_skipped(self, tmp_path) -> None:
        """Pairs with incompatible landmark dimensions should be skipped gracefully."""
        _write_sample(tmp_path / "a.json", "hello", [[[0.0, 0.0]]])  # 2D
        _write_sample(tmp_path / "b.json", "hello", [[[0.0, 0.0, 0.0]]])  # 3D

        # Should not raise — incompatible pairs are skipped
        reports = find_near_duplicates(tmp_path)
        assert reports == []

    def test_threshold_parameter(self, tmp_path) -> None:
        """Increasing threshold should eventually flag near-but-not-identical pairs."""
        frames_a = [[[0.0, 0.0]], [[1.0, 1.0]]]
        frames_b = [[[0.01, 0.01]], [[1.01, 1.01]]]  # mean dist ~0.014
        _write_sample(tmp_path / "a.json", "hello", frames_a)
        _write_sample(tmp_path / "b.json", "hello", frames_b)

        # Strict: not flagged
        reports_strict = find_near_duplicates(tmp_path, distance_threshold=0.001)
        assert reports_strict == []

        # Loose: flagged
        reports_loose = find_near_duplicates(tmp_path, distance_threshold=0.02)
        assert len(reports_loose) == 1

    def test_multiple_duplicates(self, tmp_path) -> None:
        """Multiple near-duplicate pairs should all be reported."""
        frames = [[[0.0]], [[1.0]]]
        _write_sample(tmp_path / "a.json", "hello", frames)
        _write_sample(tmp_path / "b.json", "hello", frames)
        _write_sample(tmp_path / "c.json", "thanks", frames)  # same frames, different gloss

        # Different gloss, same frames → not a near duplicate
        reports = find_near_duplicates(tmp_path)
        assert len(reports) == 1
        assert reports[0].gloss == "hello"

    def test_report_as_dict(self, tmp_path) -> None:
        """NearDuplicateReport.as_dict() should return a serialisable dict."""
        frames = [[[0.0]], [[1.0]]]
        _write_sample(tmp_path / "a.json", "hello", frames)
        _write_sample(tmp_path / "b.json", "hello", frames)

        reports = find_near_duplicates(tmp_path)
        d = reports[0].as_dict()
        assert isinstance(d, dict)
        assert d["is_near_duplicate"] is True
        assert d["gloss"] == "hello"


class TestFindDuplicatesCLI:
    def test_cli_clean_pass(self, tmp_path) -> None:
        """CLI exits 0 when no duplicates found."""
        _write_sample(tmp_path / "hello.json", "hello", [[[0.0]], [[1.0]]])
        _write_sample(tmp_path / "thanks.json", "thanks", [[[5.0]], [[6.0]]])

        result = CliRunner().invoke(
            app,
            ["gloss", "find-duplicates", "--directory", str(tmp_path)],
        )
        assert result.exit_code == 0
        assert "No near-duplicates found" in result.stdout

    def test_cli_finds_duplicates_and_fails(self, tmp_path) -> None:
        """CLI exits 1 and prints a table when duplicates are found."""
        frames = [[[0.0, 0.0]], [[1.0, 1.0]]]
        _write_sample(tmp_path / "a.json", "hello", frames)
        _write_sample(tmp_path / "b.json", "hello", frames)

        result = CliRunner().invoke(
            app,
            ["gloss", "find-duplicates", "--directory", str(tmp_path)],
        )
        assert result.exit_code == 1
        assert "Near-duplicate" in result.stdout
        assert "hello" in result.stdout

    def test_cli_report_flag_outputs_json(self, tmp_path) -> None:
        """--report flag outputs machine-readable JSON."""
        frames = [[[0.0]], [[1.0]]]
        _write_sample(tmp_path / "a.json", "hello", frames)
        _write_sample(tmp_path / "b.json", "hello", frames)

        result = CliRunner().invoke(
            app,
            ["gloss", "find-duplicates", "--directory", str(tmp_path), "--report"],
        )
        assert result.exit_code == 1
        assert '"is_near_duplicate": true' in result.stdout
        assert '"gloss": "hello"' in result.stdout

    def test_cli_threshold_option(self, tmp_path) -> None:
        """Custom threshold is respected by CLI."""
        frames_a = [[[0.0]], [[1.0]]]
        frames_b = [[[0.005]], [[1.005]]]  # mean dist ≈ 0.007
        _write_sample(tmp_path / "a.json", "hello", frames_a)
        _write_sample(tmp_path / "b.json", "hello", frames_b)

        # Default threshold (0.001) — not flagged
        result_strict = CliRunner().invoke(
            app,
            ["gloss", "find-duplicates", "--directory", str(tmp_path), "--threshold", "0.001"],
        )
        assert result_strict.exit_code == 0

        # Higher threshold — flagged
        result_loose = CliRunner().invoke(
            app,
            ["gloss", "find-duplicates", "--directory", str(tmp_path), "--threshold", "0.02"],
        )
        assert result_loose.exit_code == 1