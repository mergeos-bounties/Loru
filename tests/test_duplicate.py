from __future__ import annotations

import json
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from loru.cli import app
from loru.data.duplicate import DISTANCE_THRESHOLD, find_near_duplicates, has_near_duplicates


def _write_sample(path: Path, gloss: str, frames: list[list[float]]) -> None:
    path.write_text(json.dumps({"gloss": gloss, "frames": frames}), encoding="utf-8")


def test_identical_same_gloss_flagged() -> None:
    """Identical frames for same gloss should be flagged as near-duplicate."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        frames = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        _write_sample(tmp_path / "a.json", "hello", frames)
        _write_sample(tmp_path / "b.json", "hello", frames)

        dupes = find_near_duplicates(tmp_path, threshold=DISTANCE_THRESHOLD)
        assert len(dupes) == 1
        assert dupes[0].gloss == "hello"
        assert dupes[0].mean_distance == 0.0


def test_near_identical_not_flagged_at_strict_threshold() -> None:
    """Near-identical frames (small noise) should NOT be flagged at default strict threshold."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        frames_a = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        # Difference of 0.002 per coordinate -> distance ~0.002 > 0.001 threshold
        frames_b = [[1.002, 2.002, 3.002], [4.002, 5.002, 6.002], [7.002, 8.002, 9.002]]
        _write_sample(tmp_path / "a.json", "hello", frames_a)
        _write_sample(tmp_path / "b.json", "hello", frames_b)

        dupes = find_near_duplicates(tmp_path, threshold=DISTANCE_THRESHOLD)
        assert len(dupes) == 0


def test_near_identical_flagged_at_looser_threshold() -> None:
    """Near-identical frames SHOULD be flagged with a looser threshold."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        frames_a = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        frames_b = [[1.001, 2.001, 3.001], [4.001, 5.001, 6.001], [7.001, 8.001, 9.001]]
        _write_sample(tmp_path / "a.json", "hello", frames_a)
        _write_sample(tmp_path / "b.json", "hello", frames_b)

        dupes = find_near_duplicates(tmp_path, threshold=0.01)
        assert len(dupes) == 1


def test_different_gloss_excluded_even_with_identical_frames() -> None:
    """Different gloss should be excluded even if frames are identical."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        frames = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        _write_sample(tmp_path / "a.json", "hello", frames)
        _write_sample(tmp_path / "b.json", "thanks", frames)

        dupes = find_near_duplicates(tmp_path, threshold=DISTANCE_THRESHOLD)
        assert len(dupes) == 0


def test_incompatible_dimensions_skipped_gracefully() -> None:
    """Files with incompatible feature dimensions should be skipped without error."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        frames_a = [[1.0, 2.0, 3.0]]  # 3D
        frames_b = [[1.0, 2.0]]        # 2D
        _write_sample(tmp_path / "a.json", "hello", frames_a)
        _write_sample(tmp_path / "b.json", "hello", frames_b)

        dupes = find_near_duplicates(tmp_path, threshold=DISTANCE_THRESHOLD)
        assert len(dupes) == 0


def test_threshold_tuning() -> None:
    """Threshold parameter should control detection sensitivity."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        frames_a = [[1.0, 2.0], [3.0, 4.0]]
        frames_b = [[1.1, 2.1], [3.1, 4.1]]  # distance ~0.1
        _write_sample(tmp_path / "a.json", "hello", frames_a)
        _write_sample(tmp_path / "b.json", "hello", frames_b)

        # Strict threshold - not detected
        dupes_strict = find_near_duplicates(tmp_path, threshold=0.05)
        assert len(dupes_strict) == 0

        # Loose threshold - detected
        dupes_loose = find_near_duplicates(tmp_path, threshold=0.2)
        assert len(dupes_loose) == 1


def test_has_near_duplicates_returns_bool() -> None:
    """has_near_duplicates should return True/False correctly."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        frames = [[1.0, 2.0], [3.0, 4.0]]
        _write_sample(tmp_path / "a.json", "hello", frames)
        _write_sample(tmp_path / "b.json", "hello", frames)

        assert has_near_duplicates(tmp_path, threshold=DISTANCE_THRESHOLD) is True

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        frames_a = [[1.0, 2.0], [3.0, 4.0]]
        frames_b = [[10.0, 20.0], [30.0, 40.0]]
        _write_sample(tmp_path / "a.json", "hello", frames_a)
        _write_sample(tmp_path / "b.json", "hello", frames_b)

        assert has_near_duplicates(tmp_path, threshold=DISTANCE_THRESHOLD) is False


def test_empty_directory_returns_empty() -> None:
    """Empty directory should return empty list."""
    with tempfile.TemporaryDirectory() as tmp:
        dupes = find_near_duplicates(Path(tmp))
        assert dupes == []


def test_single_file_per_gloss_returns_empty() -> None:
    """Single file per gloss should return empty list."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        frames = [[1.0, 2.0], [3.0, 4.0]]
        _write_sample(tmp_path / "a.json", "hello", frames)

        dupes = find_near_duplicates(tmp_path)
        assert dupes == []


def test_cli_exit_code_zero_when_clean(tmp_path) -> None:
    """CLI exits 0 when no duplicates found."""
    frames_a = [[1.0, 2.0], [3.0, 4.0]]
    frames_b = [[10.0, 20.0], [30.0, 40.0]]
    sample_a = tmp_path / "a.json"
    sample_b = tmp_path / "b.json"
    _write_sample(sample_a, "hello", frames_a)
    _write_sample(sample_b, "hello", frames_b)

    runner = CliRunner()
    result = runner.invoke(app, ["gloss", "find-duplicates", "--directory", str(tmp_path)])
    assert result.exit_code == 0


def test_cli_exit_code_one_when_duplicates_found(tmp_path) -> None:
    """CLI exits 1 when duplicates found."""
    frames = [[1.0, 2.0], [3.0, 4.0]]
    sample_a = tmp_path / "a.json"
    sample_b = tmp_path / "b.json"
    _write_sample(sample_a, "hello", frames)
    _write_sample(sample_b, "hello", frames)

    runner = CliRunner()
    result = runner.invoke(app, ["gloss", "find-duplicates", "--directory", str(tmp_path)])
    assert result.exit_code == 1


def test_cli_json_report_output(tmp_path) -> None:
    """CLI --report outputs valid JSON."""
    frames = [[1.0, 2.0], [3.0, 4.0]]
    sample_a = tmp_path / "a.json"
    sample_b = tmp_path / "b.json"
    _write_sample(sample_a, "hello", frames)
    _write_sample(sample_b, "hello", frames)

    runner = CliRunner()
    result = runner.invoke(app, ["gloss", "find-duplicates", "--directory", str(tmp_path), "--report"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["gloss"] == "hello"
    assert data[0]["mean_distance"] == 0.0


def test_cli_custom_threshold(tmp_path) -> None:
    """CLI respects custom threshold parameter."""
    frames_a = [[1.0, 2.0], [3.0, 4.0]]
    frames_b = [[1.1, 2.1], [3.1, 4.1]]
    sample_a = tmp_path / "a.json"
    sample_b = tmp_path / "b.json"
    _write_sample(sample_a, "hello", frames_a)
    _write_sample(sample_b, "hello", frames_b)

    runner = CliRunner()
    # Strict threshold - no duplicates
    result_strict = runner.invoke(app, ["gloss", "find-duplicates", "--directory", str(tmp_path), "--threshold", "0.05"])
    assert result_strict.exit_code == 0

    # Loose threshold - duplicates found
    result_loose = runner.invoke(app, ["gloss", "find-duplicates", "--directory", str(tmp_path), "--threshold", "0.2"])
    assert result_loose.exit_code == 1