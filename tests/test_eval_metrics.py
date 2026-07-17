"""Tests for evaluation metrics module."""
from __future__ import annotations

from pathlib import Path

from loru.eval.metrics import top_k_accuracy, confusion_matrix, evaluate_samples, generate_report


def test_top_k_accuracy_perfect():
    preds = [["hello", "thanks"], ["thanks", "hello"]]
    true = ["hello", "thanks"]
    assert top_k_accuracy(preds, true, k=1) == 1.0
    assert top_k_accuracy(preds, true, k=2) == 1.0


def test_top_k_accuracy_partial():
    preds = [["hello", "thanks"], ["hello", "thanks"]]
    true = ["hello", "thanks"]
    assert top_k_accuracy(preds, true, k=1) == 0.5
    assert top_k_accuracy(preds, true, k=2) == 1.0


def test_top_k_accuracy_empty():
    assert top_k_accuracy([], [], k=1) == 0.0


def test_confusion_matrix_basic():
    # confusion_matrix returns {true_label: {predicted_label: count}}
    # Inputs: predictions=["a","b","a"], true_labels=["a","b","b"]
    #   sample 1: true=a, pred=a  -> matrix[a][a] += 1
    #   sample 2: true=b, pred=b  -> matrix[b][b] += 1
    #   sample 3: true=b, pred=a  -> matrix[b][a] += 1
    cm = confusion_matrix(["a", "b", "a"], ["a", "b", "b"])
    assert cm["a"]["a"] == 1   # sample 1 (correct prediction)
    assert cm["a"]["b"] == 0   # no sample has true=a, pred=b
    assert cm["b"]["a"] == 1   # sample 3 (misclassification)
    assert cm["b"]["b"] == 1   # sample 2 (correct prediction)


def test_confusion_matrix_with_labels():
    cm = confusion_matrix(["a"], ["a"], labels=["a", "b", "c"])
    assert cm["a"]["a"] == 1
    assert cm["b"]["b"] == 0
    assert cm["c"]["c"] == 0


def test_evaluate_samples_returns_dict():
    result = evaluate_samples()
    assert "total_samples" in result
    assert result["total_samples"] > 0
    assert "top1_accuracy" in result
    assert "top5_accuracy" in result
    assert "confusion_matrix" in result
    assert "per_class_accuracy" in result


def test_generate_report_saves_json(tmp_path: Path):
    out = tmp_path / "metrics.json"
    generate_report(output_path=out)  # side effect: writes JSON
    assert out.exists()
    import json
    saved = json.loads(out.read_text())
    assert "top1_accuracy" in saved
    assert "total_samples" in saved
