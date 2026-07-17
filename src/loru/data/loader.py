from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from loru.config import SAMPLES_DIR


def list_sample_files(directory: Path | None = None) -> list[Path]:
    root = directory or SAMPLES_DIR
    if not root.exists():
        return []
    return sorted(root.glob("*.json"))


def _load_payload(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"sample must be a JSON object: {path}")
    return payload


def load_sequence(path: Path) -> tuple[str, np.ndarray]:
    payload = _load_payload(path)
    gloss = str(payload.get("gloss") or path.stem).lower()
    frames = np.asarray(payload.get("frames") or [], dtype=np.float64)
    return gloss, frames


def sequence_summary(path: Path) -> dict:
    payload = _load_payload(path)
    gloss = str(payload.get("gloss") or path.stem).lower()
    frames = np.asarray(payload.get("frames") or [], dtype=np.float64)
    return {
        "path": str(path),
        "gloss": gloss,
        "language": str(payload.get("language") or "unknown"),
        "frames": int(frames.shape[0]) if frames.ndim >= 1 else 0,
        "feature_dim": int(frames.reshape(frames.shape[0], -1).shape[1]) if frames.size else 0,
    }
