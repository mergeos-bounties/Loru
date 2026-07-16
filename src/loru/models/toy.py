from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from loru.models.vocab import DEFAULT_GLOSS, id_to_gloss


class ToySignClassifier:
    """
    Offline demo model: mean landmark vector → nearest prototype.

    Replaced in later bounties by MediaPipe + real sequence models.
    """

    def __init__(self, prototypes: dict[str, np.ndarray] | None = None):
        self.prototypes = prototypes or {}

    @classmethod
    def from_samples(cls, sample_paths: list[Path]) -> "ToySignClassifier":
        buckets: dict[str, list[np.ndarray]] = {}
        for path in sample_paths:
            payload = json.loads(path.read_text(encoding="utf-8"))
            gloss = str(payload.get("gloss") or path.stem).lower()
            frames = np.asarray(payload.get("frames") or [], dtype=np.float64)
            if frames.size == 0:
                continue
            feature = frames.reshape(frames.shape[0], -1).mean(axis=0)
            buckets.setdefault(gloss, []).append(feature)
        prototypes = {
            gloss: np.mean(np.stack(vectors), axis=0)
            for gloss, vectors in buckets.items()
            if vectors
        }
        # Ensure all default glosses have a zero prototype if missing
        dim = next(iter(prototypes.values())).shape[0] if prototypes else 6
        for gloss in DEFAULT_GLOSS:
            prototypes.setdefault(gloss, np.zeros(dim, dtype=np.float64))
        return cls(prototypes)

    def predict(self, frames: np.ndarray) -> tuple[str, float]:
        ranked = self.predict_top_k(frames, k=1)
        if not ranked:
            return "unknown", 0.0
        return ranked[0]

    def predict_top_k(self, frames: np.ndarray, k: int = 3) -> list[tuple[str, float]]:
        if frames.size == 0:
            return []
        feature = frames.reshape(frames.shape[0], -1).mean(axis=0)
        scored: list[tuple[str, float]] = []
        for gloss, proto in self.prototypes.items():
            # cosine similarity with zero-safe norm
            a = feature
            b = proto
            denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
            score = float(np.dot(a, b) / denom)
            # map raw cosine [-1,1] roughly into [0,1]
            confidence = max(0.0, min(1.0, (score + 1.0) / 2.0))
            label = id_to_gloss(DEFAULT_GLOSS.index(gloss)) if gloss in DEFAULT_GLOSS else gloss
            scored.append((label, confidence))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[: max(1, k)]
