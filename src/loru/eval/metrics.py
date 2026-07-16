from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Sequence

from rich.table import Table

from loru.data.loader import load_sequence
from loru.models.toy import ToySignClassifier


def top_k_hit(true_label: str, predicted_labels: Sequence[str], k: int) -> bool:
    """Return whether true_label appears in the first k predicted labels."""
    if k < 1:
        raise ValueError("k must be >= 1")
    return true_label in list(predicted_labels)[:k]


def top_k_accuracy(y_true: Sequence[str], y_pred_ranked: Sequence[Sequence[str]], k: int) -> float:
    """Compute top-k accuracy from true labels and ranked prediction labels."""
    if len(y_true) != len(y_pred_ranked):
        raise ValueError("y_true and y_pred_ranked must have the same length")
    if not y_true:
        return 0.0
    hits = sum(1 for true, ranked in zip(y_true, y_pred_ranked) if top_k_hit(true, ranked, k))
    return hits / len(y_true)


def confusion_matrix(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str] | None = None,
) -> dict[str, dict[str, int]]:
    """Build a row=true, column=predicted confusion matrix."""
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    ordered = list(labels) if labels is not None else sorted(set(y_true) | set(y_pred))
    matrix: dict[str, dict[str, int]] = {
        label: {pred: 0 for pred in ordered}
        for label in ordered
    }
    for true, pred in zip(y_true, y_pred):
        matrix.setdefault(true, {label: 0 for label in ordered})
        if pred not in matrix[true]:
            for row in matrix.values():
                row.setdefault(pred, 0)
        matrix[true][pred] += 1
    return matrix


def evaluate_samples(
    sample_paths: Iterable[Path],
    k_values: Sequence[int] = (1, 3, 5),
) -> dict[str, Any]:
    """Evaluate the toy classifier over local sample files."""
    files = sorted(sample_paths)
    if not files:
        return {
            "n": 0,
            "labels": [],
            "top_k_accuracy": {},
            "confusion_matrix": {},
            "samples": [],
        }

    max_k = max(k_values) if k_values else 1
    classifier = ToySignClassifier.from_samples(files)
    rows: list[dict[str, Any]] = []
    y_true: list[str] = []
    ranked_labels: list[list[str]] = []

    for path in files:
        true_label, frames = load_sequence(path)
        ranked = classifier.predict_top_k(frames, k=max_k)
        predictions = [
            {"gloss": gloss, "confidence": round(confidence, 4)}
            for gloss, confidence in ranked
        ]
        labels = [item["gloss"] for item in predictions]
        y_true.append(true_label)
        ranked_labels.append(labels)
        rows.append(
            {
                "file": path.name,
                "true_gloss": true_label,
                "predicted_gloss": labels[0] if labels else "unknown",
                "top_predictions": predictions,
            }
        )

    labels = sorted(set(y_true) | {row["predicted_gloss"] for row in rows})
    top_k = {
        f"top_{k}": round(top_k_accuracy(y_true, ranked_labels, k), 4)
        for k in k_values
    }
    return {
        "n": len(rows),
        "labels": labels,
        "top_k_accuracy": top_k,
        "confusion_matrix": confusion_matrix(
            y_true,
            [row["predicted_gloss"] for row in rows],
            labels=labels,
        ),
        "samples": rows,
    }


def confusion_matrix_table(matrix: dict[str, dict[str, int]], labels: Sequence[str]) -> Table:
    """Render non-zero confusion matrix cells as a compact Rich table."""
    table = Table(title="Confusion matrix")
    table.add_column("true")
    table.add_column("predicted")
    table.add_column("count", justify="right")
    for true_label in labels:
        row = matrix.get(true_label, {})
        for pred_label in labels:
            count = row.get(pred_label, 0)
            if count:
                table.add_row(true_label, pred_label, str(count))
    return table
