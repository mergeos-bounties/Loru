from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from loru.api.app import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["gloss_count"] >= 10


def test_sentence() -> None:
    r = client.post("/infer/sentence", json={"glosses": ["hello", "friend"]})
    assert r.status_code == 200
    assert "text" in r.json()


def test_voice() -> None:
    # 21 landmarks × 3 coordinates = 63-dim frame
    frame = [float(i) for i in range(63)]
    r = client.post("/infer/voice", json={"gloss": "hello", "frames": [frame, frame]})
    assert r.status_code == 200
    data = r.json()
    assert "audio_path" in data
    assert "text" in data
    assert "predicted_gloss" in data


def test_voice_no_frames() -> None:
    r = client.post("/infer/voice", json={})
    assert r.status_code == 400


def test_infer_text_no_frames() -> None:
    r = client.post("/infer/text", json={})
    assert r.status_code == 400
