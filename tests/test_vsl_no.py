from __future__ import annotations

import json
from pathlib import Path

from loru.data.loader import load_sequence
from loru.infer.text import gloss_to_sentence
from loru.models.vocab import DEFAULT_GLOSS

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "data" / "samples"


def test_vsl_no_sample_exists_and_loads() -> None:
    path = SAMPLES_DIR / "vsl_no.json"
    assert path.exists()

    with open(path) as f:
        raw = json.load(f)

    assert raw["gloss"] == "vsl_no"
    assert raw["language"] == "vsl"
    assert raw["fps"] == 15
    assert "contributor-capture" in raw["source"]

    gloss, frames = load_sequence(path)
    assert gloss == "vsl_no"
    assert frames.ndim == 3
    assert frames.shape[0] >= 6
    assert frames.shape[1:] == (21, 3)


def test_vsl_no_registered_in_vocab() -> None:
    assert "vsl_no" in DEFAULT_GLOSS


def test_vsl_no_sentence_template() -> None:
    assert gloss_to_sentence("vsl_no") == "No."


def test_vsl_no_frames_are_distinct() -> None:
    path = SAMPLES_DIR / "vsl_no.json"
    with open(path) as f:
        raw = json.load(f)
    frames = raw["frames"]
    assert len(frames) >= 6
    assert len({tuple(tuple(p) for p in f) for f in frames}) == len(frames)
