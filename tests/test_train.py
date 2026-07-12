from __future__ import annotations

from pathlib import Path

from loru.train.toy_train import train_toy


def test_train_toy_report(tmp_path: Path, monkeypatch) -> None:
    # train_toy imports RUNS_DIR at module load; patch the module binding
    import loru.train.toy_train as toy_train_mod

    monkeypatch.setattr(toy_train_mod, "RUNS_DIR", tmp_path / "runs")
    report = train_toy(epochs=2)
    assert report["history"][-1]["accuracy"] >= 0.8
    path = Path(report["report_path"])
    assert path.exists()
    assert "ToySignClassifier" in path.read_text(encoding="utf-8")
