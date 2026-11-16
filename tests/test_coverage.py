import pytest
import os
import json
import shutil
from pathlib import Path
from loru.cli.coverage import get_existing_samples
from loru.vocab import DEFAULT_GLOSS

@pytest.fixture
def temp_samples_dir(tmp_path):
    """
    Creates a temporary directory structure for testing sample detection.
    """
    samples_dir = tmp_path / "data" / "samples"
    samples_dir.mkdir(parents=True)
    
    # Create some dummy sample files
    (samples_dir / "hello.json").write_text("{}")
    (samples_dir / "again.json").write_text("{}")
    
    # Create a subdirectory with a sample
    asl_dir = samples_dir / "asl"
    asl_dir.mkdir()
    (asl_dir / "fingerspell_a.json").write_text("{}")
    
    return str(samples_dir)

def test_get_existing_samples(temp_samples_dir):
    """
    Verifies that the scanner correctly identifies files in root and subdirectories.
    """
    found = get_existing_samples(temp_samples_dir)
    
    assert "hello" in found
    assert "again" in found
    assert "fingerspell_a" in found
    assert "goodbye" not in found
    assert len(found) == 3

def test_vocab_completeness():
    """
    Ensures DEFAULT_GLOSS is defined and is a list.
    """
    assert isinstance(DEFAULT_GLOSS, list)
    assert len(DEFAULT_GLOSS) > 0
    assert "hello" in DEFAULT_GLOSS

def test_coverage_logic_with_missing_files(temp_samples_dir):
    """
    Tests the logic of comparing existing files against the vocab.
    """
    existing = get_existing_samples(temp_samples_dir)
    
    # 'hello' is in DEFAULT_GLOSS and in our temp_samples_dir
    assert "hello" in DEFAULT_GLOSS
    assert "hello" in existing
    
    # 'mother' is in DEFAULT_GLOSS but NOT in our temp_samples_dir
    assert "mother" in DEFAULT_GLOSS
    assert "mother" not in existing
