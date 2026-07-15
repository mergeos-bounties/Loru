from __future__ import annotations

# Runnable demo gloss vocabulary (isolated signs with bundled synthetic samples).
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
    "goodbye",
    "sorry",
    "stop",
    "want",
    "need",
    "happy",
    "sad",
    "mother",
    "father",
    "friend",
    "eat_food",
    "drink",
    "home",
    "school",
    "go",
    "come",
    "see",
    "know",
    "big",
    "small",
    "welcome",
    "maybe",
    "wait",
    "today",
    "understand",
    "again",
    "more",
    "finish",
    "what",
    "where",
    "how",
    "why",
    "family",
    "work",
    "later",
    "tomorrow",
    "yesterday",
    "outside",    "inside",
    "night",
    "morning",
    "afternoon",
    "evening",
    "soon",
    "always",
    "never",
    "sometimes",
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
