"""Tests for #224: export vocab CSV for teachers."""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from loru.cli import data_export_csv


def test_export_csv_writes_file() -> None:
    """data export-csv writes a CSV file."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "test_vocab.csv"
        data_export_csv(out=out)
        assert out.exists()
        text = out.read_text(encoding="utf-8")
        assert "index,gloss,has_sample" in text


def test_export_csv_has_correct_header() -> None:
    """CSV has expected columns."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "test_vocab.csv"
        data_export_csv(out=out)
        with open(out, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == {"index", "gloss", "has_sample"}


def test_export_csv_every_gloss_present() -> None:
    """Every gloss from DEFAULT_GLOSS is in the CSV."""
    from loru.models.vocab import DEFAULT_GLOSS

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "test_vocab.csv"
        data_export_csv(out=out)
        with open(out, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == len(DEFAULT_GLOSS)
        for i, g in enumerate(DEFAULT_GLOSS):
            assert rows[i]["gloss"] == g
            assert rows[i]["index"] == str(i)
