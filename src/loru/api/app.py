"""Optional FastAPI app: `uvicorn loru.api.app:app`."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from loru import __version__
from loru.infer.text import gloss_to_sentence, multi_gloss_to_sentence, sign_to_text
from loru.models.vocab import DEFAULT_GLOSS
from loru.voice.tts import get_default_tts

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise ImportError("Install loru[api] for FastAPI support") from exc

app = FastAPI(title="Loru", version=__version__)


class SequenceBody(BaseModel):
    """Minimal sequence payload (same shape as sample JSON)."""

    gloss: str | None = None
    frames: list = Field(default_factory=list)
    language: str = "demo-asl"


class GlossBody(BaseModel):
    glosses: list[str] = Field(..., min_length=1)


class VoiceBody(BaseModel):
    """Text payload for text-to-speech conversion."""

    text: str = Field(..., min_length=1, description="Text to convert to speech")
    language: str = "en"


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "loru",
        "version": __version__,
        "gloss_count": len(DEFAULT_GLOSS),
    }


@app.get("/vocab")
def vocab() -> dict:
    return {"glosses": DEFAULT_GLOSS}


@app.post("/infer/text")
def infer_text(body: SequenceBody) -> dict:
    if not body.frames:
        raise HTTPException(400, "frames required")
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "seq.json"
        import json

        path.write_text(
            json.dumps(
                {
                    "gloss": body.gloss or "unknown",
                    "language": body.language,
                    "frames": body.frames,
                }
            ),
            encoding="utf-8",
        )
        return sign_to_text(path)


@app.post("/infer/sentence")
def infer_sentence(body: GlossBody) -> dict:
    return {
        "glosses": body.glosses,
        "text": multi_gloss_to_sentence(body.glosses),
        "single": [gloss_to_sentence(g) for g in body.glosses],
    }


@app.post("/infer/voice")
def infer_voice(body: VoiceBody) -> dict:
    """Convert text to speech audio.

    Returns the audio file path and metadata. The audio is generated using
    the configured TTS backend (see ``LORU_TTS`` env var).
    """
    with TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "voice.wav"
        tts = get_default_tts()
        audio_path = tts.speak(body.text, out_path)
        return {
            "ok": True,
            "text": body.text,
            "language": body.language,
            "audio_path": str(audio_path),
            "audio_exists": audio_path.is_file(),
            "audio_size_bytes": audio_path.stat().st_size if audio_path.is_file() else 0,
            "tts_backend": tts.backend_name,
            "duration_sec": round(
                0.35 + 0.07 * max(1, len(body.text.split())), 2
            ),
        }


@app.post("/infer/voice/file")
def infer_voice_file(body: VoiceBody) -> FileResponse:
    """Convert text to speech and return the WAV file directly."""
    with TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "voice.wav"
        tts = get_default_tts()
        audio_path = tts.speak(body.text, out_path)
        return FileResponse(
            path=str(audio_path),
            media_type="audio/wav",
            filename="voice.wav",
            headers={
                "X-Text": body.text,
                "X-TTS-Backend": tts.backend_name,
            },
        )