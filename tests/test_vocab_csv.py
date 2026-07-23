"""Tests for vocab CSV export."""

import csv
from pathlib import Path
from loru.data.vocab_csv import export_vocab_csv

def test_export_vocab_csv(tmp_path):
    output = tmp_path / 'vocab.csv'
    export_vocab_csv(output)
    
    with open(output) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) > 0
    assert 'gloss' in rows[0]
    assert 'has_sample' in rows[0]
