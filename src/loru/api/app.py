from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.responses import FileResponse

from loru import __version__
from loru.infer.text import gloss_to_sentence, multi_gloss_to_sentence, sign_to_text
from loru.models.vocab import DEFAULT_GLOSS
from loru.voice.tts import get_default_tts

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise ImportError("Install loru[api] for FastAPI support") from exc

app = FastAPI(
    title="Loru",
    description="Sign language recognition: sign-to-text and sign-to-voice inference API.",
    version=__version__,
)


class SequenceBody(BaseModel):
    """Minimal sequence payload (same shape as sample JSON)."""

    gloss: str | None = None
    frames: list = Field(default_factory=list)
    language: str = "demo-asl"


class GlossBody(BaseModel):
    glosses: list[str] = Field(..., min_length=1)


class VoiceBody(BaseModel):
    """Text to convert to speech (sign-to-voice)."""

    text: str = Field(..., min_length=1, description="Text to speak")


# ── System endpoints ──────────────────────────────────────────────────


@app.get("/health", tags=["system"])
def health() -> dict:
    """Health check — returns service status and gloss count."""
    return {
        "ok": True,
        "service": "loru",
        "version": __version__,
        "gloss_count": len(DEFAULT_GLOSS),
    }


@app.get("/vocab", tags=["system"])
def vocab() -> dict:
    """List all known glosses (sign vocabulary)."""
    return {"glosses": DEFAULT_GLOSS}


# ── Inference endpoints ───────────────────────────────────────────────


@app.post("/infer/text", tags=["inference"])
def infer_text(body: SequenceBody) -> dict:
    """Infer text from a sign language sequence (frames + optional gloss)."""
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


@app.post("/infer/sentence", tags=["inference"])
def infer_sentence(body: GlossBody) -> dict:
    """Convert a sequence of glosses into a natural-language sentence."""
    return {
        "glosses": body.glosses,
        "text": multi_gloss_to_sentence(body.glosses),
        "single": [gloss_to_sentence(g) for g in body.glosses],
    }


@app.post("/infer/voice", tags=["inference"])
def infer_voice(body: VoiceBody) -> FileResponse:
    """Convert text to spoken audio (sign-to-voice).

    Returns a WAV file with the spoken text.
    Uses the configured TTS backend (stub tone by default).
    """
    tts = get_default_tts()
    out_dir = Path("/tmp") / "loru-voice"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{hash(body.text)}.wav"
    if not out_path.exists():
        tts.speak(body.text, out_path)
    return FileResponse(
        path=str(out_path),
        media_type="audio/wav",
        filename="speech.wav",
        headers={"X-Text": body.text},
    )