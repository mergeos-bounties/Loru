from __future__ import annotations

import json

import pytest

from loru.config import SAMPLES_DIR
from loru.data.loader import SamplePayload, list_sample_files, load_sequence, sequence_summary


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


def test_existing_samples_validate_against_the_schema() -> None:
    for path in list_sample_files():
        payload = json.loads(path.read_text(encoding="utf-8"))
        sample = SamplePayload.model_validate(payload)
        assert sample.gloss
        assert sample.frames


@pytest.mark.parametrize(
    "payload, error",
    [
        ({"gloss": "hello", "frames": []}, "frames"),
        ({"gloss": "", "frames": [[[0, 1, 2]]]}, "gloss"),
        ({"gloss": "hello", "frames": [[[0, 1, 2]]], "fps": 0}, "fps"),
    ],
)
def test_invalid_sample_shape_has_helpful_error(tmp_path, payload, error) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid sample shape") as exc_info:
        load_sequence(path)
    assert error in str(exc_info.value)
