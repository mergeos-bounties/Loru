from __future__ import annotations

from pathlib import Path

from loru.data.loader import list_sample_files, load_sequence
from loru.models.toy import ToySignClassifier


def build_demo_classifier() -> ToySignClassifier:
    return ToySignClassifier.from_samples(list_sample_files())


def sign_to_text(sequence_path: Path, classifier: ToySignClassifier | None = None) -> dict:
    model = classifier or build_demo_classifier()
    gloss_true, frames = load_sequence(sequence_path)
    pred, confidence = model.predict(frames)
    # Natural language expansion (stub)
    text = gloss_to_sentence(pred)
    return {
        "true_gloss": gloss_true,
        "predicted_gloss": pred,
        "confidence": round(confidence, 4),
        "text": text,
        "source": str(sequence_path),
    }


def gloss_to_sentence(gloss: str) -> str:
    templates = {
        "hello": "Hello!",
        "thanks": "Thank you.",
        "yes": "Yes.",
        "no": "No.",
        "help": "I need help.",
        "please": "Please.",
        "love": "I love this.",
        "name": "What is your name?",
        "water": "I want water.",
        "good": "That is good.",
        "handshape_g": "Handshape G.",
    }
    return templates.get(gloss.lower(), gloss.replace("_", " ").strip().capitalize() + ".")
