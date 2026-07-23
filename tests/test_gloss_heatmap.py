"""Tests for gloss heatmap."""

from loru.data.gloss_heatmap import show_gloss_coverage

def test_show_gloss_coverage(capsys):
    show_gloss_coverage()
    captured = capsys.readouterr()
    assert "Coverage:" in captured.out
