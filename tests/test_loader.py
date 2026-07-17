from __future__ import annotations

from loru.config import SAMPLES_DIR
from loru.data.loader import list_sample_files, load_sequence, sequence_summary


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
