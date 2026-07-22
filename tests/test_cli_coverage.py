"""Tests for gloss coverage CLI command."""
import json
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from loru.cli import app

runner = CliRunner()


@pytest.fixture
def samples_tree() -> Path:
    """Create a minimal samples directory with some glosses covered."""
    base = Path(tempfile.mkdtemp())
    (base / "hello.json").write_text(json.dumps({"gloss": "hello", "frames": [[0, 0, 0]]}))
    (base / "thanks.json").write_text(json.dumps({"gloss": "thanks", "frames": [[0, 0, 0]]}))
    # subdirectory with language-specific samples
    asl_dir = base / "asl"
    asl_dir.mkdir()
    (asl_dir / "yes.json").write_text(
        json.dumps({"gloss": "yes", "language": "asl", "frames": [[0, 0, 0]]})
    )
    yield base
    import shutil
    shutil.rmtree(base)


def test_coverage_shows_summary(samples_tree: Path):
    result = runner.invoke(app, ["gloss", "coverage", "--dir", str(samples_tree)])
    assert result.exit_code == 1  # not 100% covered
    assert "hello" in result.stdout
    assert "thanks" in result.stdout
    assert "yes" in result.stdout


def test_coverage_missing_only(samples_tree: Path):
    result = runner.invoke(app, ["gloss", "coverage", "--dir", str(samples_tree), "--missing"])
    assert result.exit_code == 1
    # should list missing glosses
    assert "missing" in result.stdout.lower()


def test_coverage_all_covered_exits_zero(tmp_path: Path):
    """When all DEFAULT_GLOSS entries have samples, exit code is 0."""
    from loru.models.vocab import DEFAULT_GLOSS
    for g in DEFAULT_GLOSS:
        (tmp_path / f"{g}.json").write_text(json.dumps({"gloss": g, "frames": [[0, 0, 0]]}))
    result = runner.invoke(app, ["gloss", "coverage", "--dir", str(tmp_path)])
    assert result.exit_code == 0


def test_coverage_scans_subdirectories(samples_tree: Path):
    """The coverage command should find samples in subdirectories like asl/."""
    result = runner.invoke(app, ["gloss", "coverage", "--dir", str(samples_tree)])
    # 'yes' is in asl/ subdirectory — should be found
    assert "yes" in result.stdout
