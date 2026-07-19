from __future__ import annotations

from pathlib import Path

from loru.data.loader import list_sample_files, load_sequence
from loru.models.toy import ToySignClassifier

TEMPLATES = {
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
    "goodbye": "Goodbye!",
    "sorry": "I am sorry.",
    "stop": "Please stop.",
    "want": "I want that.",
    "need": "I need this.",
    "happy": "I am happy.",
    "sad": "I feel sad.",
    "mother": "Mother.",
    "father": "Father.",
    "friend": "This is my friend.",
    "eat_food": "I want to eat.",
    "drink": "I want a drink.",
    "home": "I am going home.",
    "school": "I am at school.",
    "go": "Let's go.",
    "come": "Please come here.",
    "see": "I see it.",
    "know": "I know.",
    "big": "It is big.",
    "small": "It is small.",
    "welcome": "Welcome!",
    "maybe": "Maybe.",
    "wait": "Please wait.",
    "today": "Today.",
    "understand": "I understand.",
    "again": "Again.",
    "more": "I want more.",
    "finish": "I am finished.",
    "what": "What?",
    "where": "Where?",
    "how": "How?",
    "why": "Why?",
    "fingerspell_z": "Z.",
    "fingerspell_y": "Y.",
    "fingerspell_x": "X.",
    "fingerspell_w": "W.",
    "fingerspell_v": "V.",
    "fingerspell_u": "U.",
}


def build_demo_classifier() -> ToySignClassifier:
    return ToySignClassifier.from_samples(list_sample_files())


def sign_to_text(sequence_path: Path, classifier: ToySignClassifier | None = None) -> dict:
    model = classifier or build_demo_classifier()
    gloss_true, frames = load_sequence(sequence_path)
    pred, confidence = model.predict(frames)
    text = gloss_to_sentence(pred)
    return {
        "true_gloss": gloss_true,
        "predicted_gloss": pred,
        "confidence": round(confidence, 4),
        "text": text,
        "source": str(sequence_path),
    }


def gloss_to_sentence(gloss: str) -> str:
    key = gloss.lower().strip()
    if key in TEMPLATES:
        return TEMPLATES[key]
    return key.replace("_", " ").strip().capitalize() + "."


def multi_gloss_to_sentence(glosses: list[str]) -> str:
    parts = [gloss_to_sentence(g).rstrip(".") for g in glosses if g.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0] + ("." if not parts[0].endswith("!") else "")
    return " ".join(parts) + "."
