from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from loru.cli import app


runner = CliRunner()


def _write_sample(directory: Path, name: str, gloss: str, language: str, frame_count: int) -> None:
    frames = [[[float(index), 0.0, 0.0]] for index in range(frame_count)]
    payload = {"gloss": gloss, "language": language, "frames": frames}
    (directory / name).write_text(json.dumps(payload), encoding="utf-8")


def test_samples_list_filters_by_gloss_and_reports_metadata(tmp_path: Path) -> None:
    _write_sample(tmp_path, "hello.json", "Hello", "demo-asl", 2)
    _write_sample(tmp_path, "thanks.json", "thanks", "demo-asl", 3)

    result = runner.invoke(
        app,
        ["samples", "list", "--gloss", "HEL", "--directory", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "hello.json" in result.stdout
    assert "demo-asl" in result.stdout
    assert "thanks.json" not in result.stdout
    assert "2" in result.stdout


def test_samples_list_reports_empty_filter_result(tmp_path: Path) -> None:
    _write_sample(tmp_path, "hello.json", "hello", "demo-asl", 1)

    result = runner.invoke(
        app,
        ["samples", "list", "--gloss", "missing", "--directory", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "No samples matching gloss 'missing'" in result.stdout
