from __future__ import annotations

from typer.testing import CliRunner

from loru.cli import app

runner = CliRunner()


def test_heatmap_cli():
    result = runner.invoke(app, ["data", "heatmap"])
    assert result.exit_code == 0
    assert "Gloss Coverage Heatmap" in result.stdout
    assert "■" in result.stdout or "□" in result.stdout
    assert "Missing glosses:" in result.stdout

def test_duplicates_cli():
    result = runner.invoke(app, ["data", "duplicates"])
    assert result.exit_code in (0, 1) # Depends on whether dataset has dups
