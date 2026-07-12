from __future__ import annotations

from pathlib import Path

from loru.infer.text import build_demo_classifier, sign_to_text
from loru.voice.tts import get_default_tts


def sign_to_voice(sequence_path: Path, out_wav: Path) -> dict:
    text_result = sign_to_text(sequence_path, build_demo_classifier())
    tts = get_default_tts()
    audio_path = tts.speak(text_result["text"], out_wav)
    return {
        **text_result,
        "audio_path": str(audio_path),
        "audio_text_sidecar": str(Path(audio_path).with_suffix(".txt")),
    }
