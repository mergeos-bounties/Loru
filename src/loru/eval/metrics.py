"""
Evaluation metrics for Loru sign-to-text classification.

Provides:
- top_k_accuracy: top-1 and top-k accuracy
- confusion_matrix: per-class confusion matrix
- evaluate_samples: run full evaluation on sample files
- generate_report: JSON-exportable report with rich-printable summary
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from rich.console import Console
from rich.table import Table

from loru.data.loader import list_sample_files, load_sequence
from loru.infer.text import sign_to_text
from loru.models.toy import ToySignClassifier


def top_k_accuracy(
    predictions: list[list[str]],
    true_labels: list[str],
    k: int = 1,
) -> float:
    """Compute top-k accuracy.

    Args:
        predictions: List of ranked prediction lists (best first).
        true_labels: List of true gloss labels.
        k: Top-k to check.

    Returns:
        Accuracy in [0, 1].
    """
    if not predictions or not true_labels:
        return 0.0
    hits = sum(
        1 for preds, true in zip(predictions, true_labels)
        if true in preds[:k]
    )
    return hits / len(true_labels)


def confusion_matrix(
    predictions: list[str],
    true_labels: list[str],
    labels: list[str] | None = None,
) -> dict[str, dict[str, int]]:
    """Build a confusion matrix as nested dict.

    Args:
        predictions: Predicted labels.
        true_labels: True labels.
        labels: Optional label list to include (even if zero count).

    Returns:
        {true_label: {predicted_label: count}}
    """
    if labels is None:
        labels = sorted(set(true_labels) | set(predictions))

    matrix: dict[str, dict[str, int]] = {
        true: {pred: 0 for pred in labels} for true in labels
    }
    for true, pred in zip(true_labels, predictions):
        if true in matrix and pred in matrix[true]:
            matrix[true][pred] += 1
    return matrix


def evaluate_samples(
    sample_dir: Path | None = None,
    classifier: ToySignClassifier | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    """Run full evaluation on all sample files.

    Args:
        sample_dir: Directory with .json sample files. Defaults to SAMPLES_DIR.
        classifier: Pre-built classifier. If None, builds from samples.
        top_k: Max k for top-k accuracy.

    Returns:
        Dict with metrics, predictions, confusion matrix.
    """
    files = list_sample_files(sample_dir) if sample_dir else list_sample_files()
    if not files:
        return {"error": "No sample files found", "total": 0}

    # Build classifier if not provided
    if classifier is None:
        classifier = ToySignClassifier.from_samples(files)

    true_labels: list[str] = []
    pred_labels: list[str] = []
    ranked_preds: list[list[str]] = []
    confidences: list[float] = []
    per_sample: list[dict] = []

    for f in files:
        result = sign_to_text(f, classifier=classifier)
        true_labels.append(result["true_gloss"])
        pred_labels.append(result["predicted_gloss"])
        confidences.append(result["confidence"])

        # Get ranked predictions (top-k) from classifier
        gloss_true, frames = load_sequence(f)
        feature = frames.reshape(frames.shape[0], -1).mean(axis=0)
        scores = []
        for gloss, proto in classifier.prototypes.items():
            denom = (np.linalg.norm(feature) * np.linalg.norm(proto)) + 1e-9
            score = float(np.dot(feature, proto) / denom)
            scores.append((gloss, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        ranked_preds.append([g for g, _ in scores[:top_k]])

        per_sample.append({
            "file": str(f.name),
            "true": result["true_gloss"],
            "predicted": result["predicted_gloss"],
            "confidence": result["confidence"],
            "correct": result["true_gloss"] == result["predicted_gloss"],
        })

    # Compute metrics
    top1 = top_k_accuracy(ranked_preds, true_labels, k=1)
    topk = top_k_accuracy(ranked_preds, true_labels, k=min(top_k, len(ranked_preds[0]) if ranked_preds else 1))
    cm = confusion_matrix(pred_labels, true_labels)

    # Per-class accuracy
    per_class: dict[str, float] = {}
    class_counts = Counter(true_labels)
    class_correct = defaultdict(int)
    for true, pred in zip(true_labels, pred_labels):
        if true == pred:
            class_correct[true] += 1
    for label, count in class_counts.items():
        per_class[label] = round(class_correct[label] / count, 4) if count > 0 else 0.0

    return {
        "total_samples": len(files),
        "top1_accuracy": round(top1, 4),
        "top5_accuracy": round(topk, 4),
        "mean_confidence": round(float(np.mean(confidences)), 4) if confidences else 0.0,
        "per_class_accuracy": per_class,
        "confusion_matrix": cm,
        "per_sample": per_sample,
    }


def generate_report(
    sample_dir: Path | None = None,
    output_path: Path | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    """Generate evaluation report and optionally save to JSON.

    Args:
        sample_dir: Directory with samples.
        output_path: Path to save JSON report.
        top_k: Max k for top-k accuracy.

    Returns:
        Report dict.
    """
    console = Console()
    console.print("[bold cyan]Loru Evaluation Report[/bold cyan]")
    console.print()

    report = evaluate_samples(sample_dir=sample_dir, top_k=top_k)

    if "error" in report:
        console.print(f"[red]Error: {report['error']}[/red]")
        return report

    # Print summary table
    table = Table(title="Evaluation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Total Samples", str(report["total_samples"]))
    table.add_row("Top-1 Accuracy", f"{report['top1_accuracy']:.2%}")
    table.add_row("Top-5 Accuracy", f"{report['top5_accuracy']:.2%}")
    table.add_row("Mean Confidence", f"{report['mean_confidence']:.4f}")
    console.print(table)

    # Print confusion matrix
    cm_table = Table(title="Confusion Matrix (True → Predicted)")
    cm_table.add_column("True \\ Pred", style="cyan")
    labels = sorted(report["confusion_matrix"].keys())
    for label in labels:
        cm_table.add_column(label[:8], style="white")
    for true in labels:
        row = [true[:8]]
        for pred in labels:
            count = report["confusion_matrix"][true].get(pred, 0)
            if true == pred and count > 0:
                row.append(f"[green]{count}[/green]")
            elif count > 0:
                row.append(f"[red]{count}[/red]")
            else:
                row.append("0")
        cm_table.add_row(*row)
    console.print(cm_table)

    # Save to JSON if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, default=str),
            encoding="utf-8",
        )
        console.print(f"\n[green]Report saved to {output_path}[/green]")

    return report
