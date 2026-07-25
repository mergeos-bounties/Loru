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


def test_infer_voice() -> None:
    """POST /infer/voice returns audio metadata."""
    r = client.post("/infer/voice", json={"text": "Hello world"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["text"] == "Hello world"
    assert data["audio_exists"] is True
    assert data["audio_size_bytes"] > 44  # valid WAV header
    assert data["tts_backend"] in ("OfflineStubTTS", "Pyttsx3TTS", "EdgeTTS")


def test_infer_voice_empty_text() -> None:
    """Empty text should return 422 validation error."""
    r = client.post("/infer/voice", json={"text": ""})
    assert r.status_code == 422


def test_infer_voice_file() -> None:
    """POST /infer/voice/file returns a WAV file."""
    r = client.post("/infer/voice/file", json={"text": "Test audio"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/wav"
    assert len(r.content) > 44  # valid WAV
    assert "X-Text" in r.headers
    assert r.headers["X-Text"] == "Test audio"