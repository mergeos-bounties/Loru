from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from loru.cli import app
from loru.data.dedupe import detect_duplicates, _frame_hash, dedupe_report_table
import numpy as np


def _write_sample(path: Path, gloss: str, frames: list) -> Path:
    path.write_text(json.dumps({"gloss": gloss, "frames": frames}), encoding="utf-8")
    return path


# ── frame_hash ──────────────────────────────────────────────

def test_frame_hash_is_deterministic() -> None:
    frames = np.array([[[1.0, 2.0]], [[3.0, 4.0]]], dtype=np.float64)
    assert _frame_hash(frames) == _frame_hash(frames.copy())


def test_frame_hash_differs_for_different_content() -> None:
    a = np.array([[[0.0]]], dtype=np.float64)
    b = np.array([[[1.0]]], dtype=np.float64)
    assert _frame_hash(a) != _frame_hash(b)


# ── Exact duplicate detection ──────────────────────────────

def test_exact_duplicate_detection(tmp_path: Path) -> None:
    frames = [[[0.0, 0.0, 0.0]], [[1.0, 1.0, 1.0]]]
    _write_sample(tmp_path / "hello.json", "hello", frames)
    _write_sample(tmp_path / "hello_clone.json", "hello", frames)
    _write_sample(tmp_path / "goodbye.json", "goodbye", [[[2.0, 2.0, 2.0]]])

    report = detect_duplicates(tmp_path)

    assert report["scanned"] == 3
    assert report["exact_duplicate_groups"] == 1
    assert report["exact_duplicates"][0]["count"] == 2
    assert report["exact_duplicates"][0]["type"] == "exact"


def test_no_exact_duplicates_when_all_unique(tmp_path: Path) -> None:
    _write_sample(tmp_path / "a.json", "hello", [[[0.0]]])
    _write_sample(tmp_path / "b.json", "goodbye", [[[1.0]]])

    report = detect_duplicates(tmp_path)

    assert report["exact_duplicate_groups"] == 0
    assert report["exact_duplicates"] == []


# ── Near-duplicate detection ───────────────────────────────

def test_near_duplicate_below_threshold(tmp_path: Path) -> None:
    a = _write_sample(tmp_path / "a.json", "hello", [[[0.0, 0.0]], [[1.0, 1.0]]])
    b = _write_sample(tmp_path / "b.json", "hello_clone", [[[0.0001, 0.0002]], [[1.0001, 1.0002]]])

    report = detect_duplicates(tmp_path, near_threshold=0.01)

    assert report["near_duplicate_pairs"] >= 1
    assert report["near_duplicates"][0]["mean_distance"] <= 0.01


def test_no_near_duplicates_when_distant(tmp_path: Path) -> None:
    _write_sample(tmp_path / "a.json", "hello", [[[0.0]]])
    _write_sample(tmp_path / "b.json", "goodbye", [[[100.0]]])

    report = detect_duplicates(tmp_path, near_threshold=0.01)

    assert report["near_duplicate_pairs"] == 0


def test_identical_frames_are_both_exact_and_near(tmp_path: Path) -> None:
    frames = [[[0.0, 0.0]], [[1.0, 1.0]]]
    _write_sample(tmp_path / "a.json", "hello", frames)
    _write_sample(tmp_path / "b.json", "hello_copy", frames)

    report = detect_duplicates(tmp_path)

    assert report["exact_duplicate_groups"] == 1
    assert report["near_duplicate_pairs"] == 1
    assert report["near_duplicates"][0]["mean_distance"] == 0.0


# ── Empty directory ────────────────────────────────────────

def test_empty_directory_reports_zero(tmp_path: Path) -> None:
    report = detect_duplicates(tmp_path)
    assert report["scanned"] == 0
    assert report["exact_duplicate_groups"] == 0
    assert report["near_duplicate_pairs"] == 0


# ── Single file ────────────────────────────────────────────

def test_single_file_no_duplicates(tmp_path: Path) -> None:
    _write_sample(tmp_path / "only.json", "hello", [[[0.0]]])
    report = detect_duplicates(tmp_path)
    assert report["scanned"] == 1
    assert report["exact_duplicate_groups"] == 0
    assert report["near_duplicate_pairs"] == 0


# ── CLI integration ────────────────────────────────────────

def test_gloss_dedupe_cli(tmp_path: Path) -> None:
    frames = [[[0.0, 0.0]], [[1.0, 1.0]]]
    _write_sample(tmp_path / "a.json", "hello", frames)
    _write_sample(tmp_path / "b.json", "hello_2", frames)
    _write_sample(tmp_path / "c.json", "goodbye", [[[99.0, 99.0]]])

    runner = CliRunner()
    result = runner.invoke(app, ["gloss", "dedupe", "--directory", str(tmp_path)])

    assert result.exit_code == 0
    assert "exact-duplicate groups found" in result.stdout
    assert "1 exact-duplicate" in result.stdout


def test_gloss_dedupe_cli_json(tmp_path: Path) -> None:
    frames = [[[0.0, 0.0]], [[1.0, 1.0]]]
    _write_sample(tmp_path / "a.json", "hello", frames)
    _write_sample(tmp_path / "b.json", "hello_2", frames)

    runner = CliRunner()
    result = runner.invoke(
        app, ["gloss", "dedupe", "--directory", str(tmp_path), "--json"]
    )

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["exact_duplicate_groups"] == 1
    assert data["scanned"] == 2


def test_dedupe_cli_custom_threshold(tmp_path: Path) -> None:
    _write_sample(tmp_path / "a.json", "hello", [[[0.0]]])
    _write_sample(tmp_path / "b.json", "near", [[[0.5]]])

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "gloss",
            "dedupe",
            "--directory",
            str(tmp_path),
            "--near-threshold",
            "1.0",
        ],
    )

    assert result.exit_code == 0
    assert "near-duplicate" in result.stdout


def test_dedupe_report_table_no_duplicates(capsys) -> None:
    dedupe_report_table({
        "scanned": 5,
        "exact_duplicate_groups": 0,
        "exact_duplicates": [],
        "near_duplicate_pairs": 0,
        "near_duplicates": [],
        "threshold": 0.01,
    })
    captured = capsys.readouterr()
    assert "No exact-frame duplicates found" in captured.out
    assert "No near-duplicate" in captured.out