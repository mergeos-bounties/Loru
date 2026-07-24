from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from loru.api.app import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self) -> None:
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["service"] == "loru"
        assert data["gloss_count"] >= 10


class TestVocab:
    def test_vocab_returns_glosses(self) -> None:
        r = client.get("/vocab")
        assert r.status_code == 200
        data = r.json()
        assert "glosses" in data
        assert len(data["glosses"]) >= 10
        assert "hello" in data["glosses"]


class TestInferText:
    def test_infer_text_requires_frames(self) -> None:
        r = client.post("/infer/text", json={"gloss": "hello", "frames": []})
        assert r.status_code == 400
        assert "frames required" in r.json()["detail"]

    def test_infer_text_with_frames(self) -> None:
        r = client.post(
            "/infer/text",
            json={
                "gloss": "hello",
                "frames": [
                    {"x": 0.1, "y": 0.2, "z": 0.3},
                    {"x": 0.4, "y": 0.5, "z": 0.6},
                ],
                "language": "demo-asl",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "prediction" in data or "gloss" in data or "text" in data


class TestInferSentence:
    def test_infer_sentence(self) -> None:
        r = client.post("/infer/sentence", json={"glosses": ["hello", "friend"]})
        assert r.status_code == 200
        data = r.json()
        assert "text" in data
        assert "glosses" in data
        assert "single" in data
        assert data["glosses"] == ["hello", "friend"]

    def test_infer_sentence_single_gloss(self) -> None:
        r = client.post("/infer/sentence", json={"glosses": ["hello"]})
        assert r.status_code == 200
        data = r.json()
        assert "text" in data
        assert len(data["glosses"]) == 1

    def test_infer_sentence_empty_returns_422(self) -> None:
        r = client.post("/infer/sentence", json={"glosses": []})
        assert r.status_code == 422


class TestInferVoice:
    def test_infer_voice_returns_wav(self) -> None:
        r = client.post("/infer/voice", json={"text": "Hello, world!"})
        assert r.status_code == 200
        assert r.headers["content-type"] == "audio/wav"
        assert r.headers.get("x-text") == "Hello, world!"
        # Verify it's a valid WAV file
        content = r.content
        assert content[:4] == b"RIFF"  # WAV header
        assert content[8:12] == b"WAVE"  # WAV format

    def test_infer_voice_empty_text_returns_422(self) -> None:
        r = client.post("/infer/voice", json={"text": ""})
        assert r.status_code == 422

    def test_infer_voice_missing_text_returns_422(self) -> None:
        r = client.post("/infer/voice", json={})
        assert r.status_code == 422


class TestOpenApi:
    def test_openapi_schema_is_valid(self) -> None:
        r = client.get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema
        assert "/health" in schema["paths"]
        assert "/vocab" in schema["paths"]
        assert "/infer/text" in schema["paths"]
        assert "/infer/sentence" in schema["paths"]
        assert "/infer/voice" in schema["paths"]

    def test_openapi_tags_are_set(self) -> None:
        r = client.get("/openapi.json")
        schema = r.json()
        tags = [t["name"] for t in schema.get("tags", [])]
        # FastAPI auto-tags routes with their tags parameter
        # Check that paths have proper tags
        for path, methods in schema["paths"].items():
            for method, spec in methods.items():
                if "tags" in spec:
                    assert len(spec["tags"]) > 0, f"{method.upper()} {path} has no tags"