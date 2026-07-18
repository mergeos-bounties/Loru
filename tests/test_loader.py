from __future__ import annotations

from loru.config import SAMPLES_DIR
from loru.data.loader import list_sample_files, load_sequence, sequence_summary
from loru.infer.text import gloss_to_sentence
from loru.models.vocab import DEFAULT_GLOSS


def test_samples_exist() -> None:
    files = list_sample_files()
    assert len(files) >= 10
    assert SAMPLES_DIR.exists()


def test_load_sequence_shapes() -> None:
    path = list_sample_files()[0]
    gloss, frames = load_sequence(path)
    assert isinstance(gloss, str) and gloss
    assert frames.ndim == 3  # frames, landmarks, xyz
    assert frames.shape[0] >= 1
    summary = sequence_summary(path)
    assert summary["gloss"] == gloss
    assert summary["language"]
    assert summary["frames"] == frames.shape[0]


def test_school_sign_pack_has_sample_vocab_and_unique_frames() -> None:
    path = SAMPLES_DIR / "school.json"

    assert path.exists()
    assert "school" in DEFAULT_GLOSS
    assert gloss_to_sentence("school") == "I am at school."

    gloss, frames = load_sequence(path)

    assert gloss == "school"
    assert frames.ndim == 3
    assert frames.shape[0] >= 6
    assert frames.shape[1:] == (21, 3)
    assert len({frame.tobytes() for frame in frames}) == frames.shape[0]
