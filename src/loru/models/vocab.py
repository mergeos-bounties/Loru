from __future__ import annotations

# Tiny demo gloss vocabulary (isolated signs).
DEFAULT_GLOSS = [
    "hello",
    "thanks",
    "yes",
    "no",
    "help",
    "please",
    "love",
    "name",
    "water",
    "good",
]


def gloss_to_id(gloss: str) -> int:
    key = gloss.strip().lower()
    if key not in DEFAULT_GLOSS:
        raise KeyError(f"unknown gloss {gloss!r}; known={DEFAULT_GLOSS}")
    return DEFAULT_GLOSS.index(key)


def id_to_gloss(idx: int) -> str:
    if idx < 0 or idx >= len(DEFAULT_GLOSS):
        return "unknown"
    return DEFAULT_GLOSS[idx]
