from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from loru import __version__
from loru.config import OUT_DIR
from loru.infer.pipeline import sign_to_voice
from loru.infer.text import gloss_to_sentence, multi_gloss_to_sentence, sign_to_text
from loru.models.vocab import DEFAULT_GLOSS

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.responses import Response
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise ImportError("Install loru[api] for FastAPI support") from exc

OPENAPI_TAGS = [
    {"name": "health", "description": "Service health and readiness probes."},
    {"name": "vocab", "description": "Default sign gloss vocabulary inspection."},
    {"name": "infer", "description": "Sign-to-text and sign-to-voice inference endpoints."},
]

app = FastAPI(
    title="Loru",
    description="Sign-to-text and sign-to-voice inference API (`loru serve` / `uvicorn loru.api.app:app`).",
    version=__version__,
    openapi_tags=OPENAPI_TAGS,
)


class SequenceBody(BaseModel):
    """Minimal sequence payload (same shape as sample JSON)."""

    gloss: str | None = None
    frames: list = Field(default_factory=list)
    language: str = "demo-asl"


class VoiceSequenceBody(SequenceBody):
    """Sequence payload for sign-to-voice synthesis."""

    return_bytes: bool = Field(
        default=False,
        description="Return raw audio/wav bytes instead of JSON metadata when true.",
    )
    output_path: str | None = Field(
        default=None,
        description="Optional destination WAV path when returning JSON metadata.",
    )


class GlossBody(BaseModel):
    glosses: list[str] = Field(..., min_length=1)


def _write_temp_sequence(body: SequenceBody, tmp_dir: str) -> Path:
    path = Path(tmp_dir) / "seq.json"
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
    return path


@app.get("/health", tags=["health"])
def health() -> dict:
    return {
        "ok": True,
        "status": "ok",
        "service": "loru",
        "version": __version__,
        "gloss_count": len(DEFAULT_GLOSS),
    }


@app.get("/vocab", tags=["vocab"])
def vocab() -> dict:
    return {"glosses": DEFAULT_GLOSS}


@app.post("/infer/text", tags=["infer"])
def infer_text(body: SequenceBody) -> dict:
    if not body.frames:
        raise HTTPException(400, "frames required")
    with TemporaryDirectory() as tmp:
        seq_path = _write_temp_sequence(body, tmp)
        return sign_to_text(seq_path)


@app.post("/infer/voice", tags=["infer"], response_model=None)
def infer_voice(
    body: VoiceSequenceBody,
    format: str = Query("json", pattern="^(json|wav)$", description="Response format: json or wav"),
) -> dict | Response:
    if not body.frames:
        raise HTTPException(400, "frames required")
    want_bytes = body.return_bytes or format == "wav"
    with TemporaryDirectory() as tmp:
        seq_path = _write_temp_sequence(body, tmp)
        if want_bytes:
            wav_target = Path(tmp) / "voice.wav"
            result = sign_to_voice(seq_path, wav_target)
            audio_bytes = Path(result["audio_path"]).read_bytes()
            return Response(content=audio_bytes, media_type="audio/wav")

        if body.output_path:
            out_wav = Path(body.output_path)
        else:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            out_wav = OUT_DIR / f"api_{body.gloss or 'infer'}.wav"
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        result = sign_to_voice(seq_path, out_wav)
        audio_file = Path(result["audio_path"])
        return {
            **result,
            "bytes_size": audio_file.stat().st_size if audio_file.exists() else 0,
        }


@app.post("/infer/sentence", tags=["infer"])
def infer_sentence(body: GlossBody) -> dict:
    return {
        "glosses": body.glosses,
        "text": multi_gloss_to_sentence(body.glosses),
        "single": [gloss_to_sentence(g) for g in body.glosses],
    }
