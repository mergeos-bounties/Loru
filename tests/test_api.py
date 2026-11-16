from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from loru.api.app import app
from loru.config import SAMPLES_DIR

client = TestClient(app)


def _sample_payload() -> dict:
    sample_path = SAMPLES_DIR / "hello.json"
    return json.loads(sample_path.read_text(encoding="utf-8"))


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["gloss_count"] >= 10


def test_sentence() -> None:
    r = client.post("/infer/sentence", json={"glosses": ["hello", "friend"]})
    assert r.status_code == 200
    assert "text" in r.json()


def test_infer_text() -> None:
    payload = _sample_payload()
    r = client.post("/infer/text", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "predicted_gloss" in data
    assert "text" in data


def test_infer_text_requires_frames() -> None:
    r = client.post("/infer/text", json={"gloss": "hello", "frames": []})
    assert r.status_code == 400


def test_infer_voice_path(tmp_path: Path) -> None:
    payload = _sample_payload()
    out_wav = tmp_path / "hello_out.wav"
    payload["output_path"] = str(out_wav)
    r = client.post("/infer/voice", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert Path(data["audio_path"]).exists()
    assert data["bytes_size"] > 44
    assert "text" in data


def test_infer_voice_wav_bytes() -> None:
    payload = _sample_payload()
    payload["return_bytes"] = True
    r = client.post("/infer/voice", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("audio/wav")
    assert r.content[:4] == b"RIFF"


def test_openapi_tags_clean() -> None:
    schema = app.openapi()
    tag_names = {t["name"] for t in schema.get("tags", [])}
    assert {"health", "vocab", "infer"} <= tag_names
    assert schema["paths"]["/health"]["get"]["tags"] == ["health"]
    assert schema["paths"]["/infer/text"]["post"]["tags"] == ["infer"]
    assert schema["paths"]["/infer/voice"]["post"]["tags"] == ["infer"]
