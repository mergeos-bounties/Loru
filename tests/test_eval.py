from __future__ import annotations

from pathlib import Path

from loru.data.loader import list_sample_files
from loru.infer.pipeline import sign_to_voice
from loru.infer.text import multi_gloss_to_sentence, sign_to_text


def test_multi_gloss() -> None:
    text = multi_gloss_to_sentence(["hello", "friend"])
    assert "Hello" in text or "hello" in text.lower()


def test_high_accuracy_on_samples() -> None:
    files = list_sample_files()
    assert len(files) >= 20
    hits = sum(1 for p in files if sign_to_text(p)["predicted_gloss"] == sign_to_text(p)["true_gloss"])
    # recompute cleanly
    hits = 0
    for p in files:
        r = sign_to_text(p)
        if r["predicted_gloss"] == r["true_gloss"]:
            hits += 1
    assert hits / len(files) >= 0.85


def test_voice_audible_wav(tmp_path: Path) -> None:
    path = list_sample_files()[0]
    out = tmp_path / "t.wav"
    sign_to_voice(path, out)
    assert out.stat().st_size > 1000
