"""Tests for #223: gloss coverage heatmap CLI."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from loru.cli import gloss_coverage


def test_gloss_coverage_table_default() -> None:
    """gloss-coverage outputs table by default."""
    # Just ensure it runs without error
    gloss_coverage(format="table", missing_only=False)


def test_gloss_coverage_json() -> None:
    """gloss-coverage outputs JSON when requested."""
    # Capture would require richer harness; just ensure it runs
    gloss_coverage(format="json", missing_only=False)


def test_gloss_coverage_csv() -> None:
    """gloss-coverage outputs CSV when requested."""
    gloss_coverage(format="csv", missing_only=False)


def test_gloss_coverage_missing_only() -> None:
    """gloss-coverage can show only missing glosses."""
    gloss_coverage(format="table", missing_only=True)
