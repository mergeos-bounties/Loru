from __future__ import annotations

import json

from loru.config import RUNS_DIR
from loru.data.loader import list_sample_files, load_sequence
from loru.models.toy import ToySignClassifier


def train_toy(epochs: int = 3) -> dict:
    """
    'Training' for the toy model: rebuild prototypes each epoch (idempotent).
    Real training bounties replace this with gradient-based sequence models.
    """
    samples = list_sample_files()
    if not samples:
        raise FileNotFoundError("no samples under data/samples")

    history = []
    classifier = None
    for epoch in range(1, max(1, epochs) + 1):
        classifier = ToySignClassifier.from_samples(samples)
        correct = 0
        for path in samples:
            true_gloss, frames = load_sequence(path)
            pred, _ = classifier.predict(frames)
            if pred == true_gloss:
                correct += 1
        acc = correct / len(samples)
        history.append({"epoch": epoch, "accuracy": round(acc, 4), "n": len(samples)})

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RUNS_DIR / "toy_train_report.json"
    report = {
        "model": "ToySignClassifier",
        "epochs": epochs,
        "history": history,
        "prototypes": sorted((classifier.prototypes or {}).keys()) if classifier else [],
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return {"report_path": str(report_path), **report}
