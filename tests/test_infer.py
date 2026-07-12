from __future__ import annotations

from pathlib import Path

from loru.data.loader import list_sample_files
from loru.infer.pipeline import sign_to_voice
from loru.infer.text import gloss_to_sentence, sign_to_text
from loru.models.toy import ToySignClassifier


def test_gloss_to_sentence_templates() -> None:
    assert "Hello" in gloss_to_sentence("hello")
    assert gloss_to_sentence("unknown_sign").endswith(".")


def test_sign_to_text_on_samples() -> None:
    files = list_sample_files()
    model = ToySignClassifier.from_samples(files)
    hits = 0
    for path in files:
        result = sign_to_text(path, model)
        assert "predicted_gloss" in result
        assert "text" in result
        assert 0.0 <= result["confidence"] <= 1.0
        if result["predicted_gloss"] == result["true_gloss"]:
            hits += 1
    # Toy prototypes should match training samples almost perfectly
    assert hits >= int(0.8 * len(files))


def test_sign_to_voice_writes_wav(tmp_path: Path) -> None:
    path = list_sample_files()[0]
    out = tmp_path / "out.wav"
    result = sign_to_voice(path, out)
    assert out.exists()
    assert out.stat().st_size > 44  # header + samples
    assert Path(result["audio_path"]).exists()
    sidecar = out.with_suffix(".txt")
    assert sidecar.exists()
    assert sidecar.read_text(encoding="utf-8").strip()
