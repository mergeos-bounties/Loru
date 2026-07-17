from __future__ import annotations

from loru.data.loader import list_sample_files
from loru.eval.metrics import (
    confusion_matrix,
    confusion_matrix_table,
    evaluate_samples,
    top_k_accuracy,
    top_k_hit,
)


def test_top_k_helpers() -> None:
    ranked = [["cat", "dog", "bird"], ["red", "green", "blue"]]
    assert top_k_hit("dog", ranked[0], k=2)
    assert not top_k_hit("bird", ranked[0], k=2)
    assert top_k_accuracy(["dog", "blue"], ranked, k=3) == 1.0
    assert top_k_accuracy(["dog", "blue"], ranked, k=1) == 0.0


def test_confusion_matrix_counts() -> None:
    matrix = confusion_matrix(
        ["hello", "hello", "thanks"],
        ["hello", "thanks", "thanks"],
        labels=["hello", "thanks"],
    )
    assert matrix["hello"]["hello"] == 1
    assert matrix["hello"]["thanks"] == 1
    assert matrix["thanks"]["thanks"] == 1


def test_evaluate_samples_report_shape() -> None:
    report = evaluate_samples(list_sample_files()[:5], k_values=(1, 3))
    assert report["n"] == 5
    assert set(report["top_k_accuracy"]) == {"top_1", "top_3"}
    assert report["top_k_accuracy"]["top_3"] >= report["top_k_accuracy"]["top_1"]
    assert report["samples"][0]["top_predictions"]
    table = confusion_matrix_table(report["confusion_matrix"], report["labels"])
    assert table.title == "Confusion matrix"
