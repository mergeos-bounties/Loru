from __future__ import annotations

import json
from pathlib import Path

from loru.data.duplicates import detect_duplicates


def test_detect_duplicates_distinct(tmp_path: Path):
    frames1 = [[float(i), 0.0, 0.0] for i in range(10)]
    frames2 = [[0.0, 0.0, 0.0]] * 5 + [[float(i), 0.0, 0.0] for i in range(2, 8)] + [[-1.0, -1.0, -1.0]] * 5
    
    f1 = tmp_path / "hello.json"
    f1.write_text(json.dumps({"gloss": "hello", "frames": frames1}))

    f2 = tmp_path / "world.json"
    f2.write_text(json.dumps({"gloss": "world", "frames": frames2}))

    dups = detect_duplicates(samples_dir=tmp_path, min_sequence_length=5)
    assert len(dups) == 1
    d = dups[0]
    assert d["file_a"] == "hello.json"
    assert d["file_b"] == "world.json"
    assert d["offset_a"] == 2
    assert d["offset_b"] == 5
    assert d["length"] == 6
