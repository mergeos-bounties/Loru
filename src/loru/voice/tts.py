from __future__ import annotations

import struct
import wave
from pathlib import Path


class TextToSpeech:
    """TTS interface. Default implementation writes a silent placeholder WAV."""

    def speak(self, text: str, out_path: Path) -> Path:
        raise NotImplementedError


class OfflineStubTTS(TextToSpeech):
    """
    Offline-safe TTS stub: writes a short silent WAV so the pipeline works
    without native audio engines. Bounties can swap in pyttsx3 / edge-tts.
    """

    def speak(self, text: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # duration scales slightly with text length
        duration_sec = min(3.0, 0.4 + 0.05 * max(1, len(text.split())))
        sample_rate = 16000
        n_samples = int(sample_rate * duration_sec)
        with wave.open(str(out_path), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            silence = struct.pack("<h", 0)
            wf.writeframes(silence * n_samples)
        # sidecar text for debugging
        out_path.with_suffix(".txt").write_text(text, encoding="utf-8")
        return out_path


def get_default_tts() -> TextToSpeech:
    return OfflineStubTTS()
