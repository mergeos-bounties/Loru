from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from loru import __version__
from loru.infer.text import gloss_to_sentence, multi_gloss_to_sentence, sign_to_text
from loru.models.vocab import DEFAULT_GLOSS

try:
    from fastapi import FastAPI, HTTPException
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
