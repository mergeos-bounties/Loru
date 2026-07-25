from __future__ import annotations

import asyncio
import math
import struct
import wave
from pathlib import Path


class TextToSpeech:
    """TTS interface."""

    def speak(self, text: str, out_path: Path) -> Path:
        raise NotImplementedError

    @property
    def backend_name(self) -> str:
        return self.__class__.__name__


class OfflineStubTTS(TextToSpeech):
    """
    Offline TTS that writes a short audible tone (not silence) so the
    sign→voice pipeline produces a real playable WAV without native engines.
    """

    def speak(self, text: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        duration_sec = min(3.0, 0.35 + 0.07 * max(1, len(text.split())))
        sample_rate = 16000
        n_samples = int(sample_rate * duration_sec)
        # simple multi-beep mapping from text length
        freq = 220 + (len(text) % 12) * 40
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            # envelope to avoid clicks
            env = min(1.0, t * 10) * min(1.0, (duration_sec - t) * 10)
            # soft square-ish tone
            val = env * 0.25 * math.sin(2 * math.pi * freq * t)
            frames += struct.pack("<h", int(val * 32767))
        with wave.open(str(out_path), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(bytes(frames))
        out_path.with_suffix(".txt").write_text(text, encoding="utf-8")
        return out_path


class Pyttsx3TTS(TextToSpeech):
    """Optional native TTS when pyttsx3 is installed (LORU_TTS=pyttsx3)."""

    def __init__(self) -> None:
        import pyttsx3  # type: ignore

        self._engine = pyttsx3.init()

    def speak(self, text: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # pyttsx3 often needs .wav path; also keep text sidecar
        self._engine.save_to_file(text, str(out_path))
        self._engine.runAndWait()
        out_path.with_suffix(".txt").write_text(text, encoding="utf-8")
        if not out_path.exists() or out_path.stat().st_size < 44:
            # fall back if engine did not write a real wav
            return OfflineStubTTS().speak(text, out_path)
        return out_path


class EdgeTTS(TextToSpeech):
    """
    Online TTS via Microsoft Edge's free TTS service (edge-tts).

    Requires the ``edge-tts`` package (``pip install loru[voice]``).
    Set ``LORU_TTS=edge`` or ``LORU_TTS=auto`` to use this backend.
    Optionally set ``LORU_TTS_VOICE`` to choose a voice (default: en-US-JennyNeural).
    """

    DEFAULT_VOICE = "en-US-JennyNeural"

    def speak(self, text: str, out_path: Path) -> Path:
        import os

        out_path.parent.mkdir(parents=True, exist_ok=True)
        voice = os.getenv("LORU_TTS_VOICE") or self.DEFAULT_VOICE

        async def _do_speak() -> None:
            import edge_tts  # type: ignore

            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(out_path))

        asyncio.run(_do_speak())
        out_path.with_suffix(".txt").write_text(text, encoding="utf-8")
        if not out_path.exists() or out_path.stat().st_size < 44:
            # fall back if edge-tts did not write a real audio file
            return OfflineStubTTS().speak(text, out_path)
        return out_path


def get_default_tts() -> TextToSpeech:
    import os

    prefer = (os.getenv("LORU_TTS") or "auto").strip().lower()
    if prefer in {"stub", "offline", "tone"}:
        return OfflineStubTTS()
    if prefer in {"edge", "edge-tts"}:
        try:
            return EdgeTTS()
        except Exception:
            if prefer != "auto":
                raise
            return OfflineStubTTS()
    if prefer in {"pyttsx3", "native", "auto"}:
        try:
            return Pyttsx3TTS()
        except Exception:
            if prefer == "pyttsx3":
                raise
            return OfflineStubTTS()
    # auto mode: try edge-tts first (better quality), fall back to pyttsx3, then stub
    try:
        return EdgeTTS()
    except Exception:
        try:
            return Pyttsx3TTS()
        except Exception:
            return OfflineStubTTS()
