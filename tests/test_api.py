import pytest
from fastapi.testclient import TestClient
from loru.api.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "loru-api"}

def test_infer_text():
    payload = {
        "frames": [
            {"landmark_0": [0.1, 0.2, 0.3]},
            {"landmark_0": [0.11, 0.21, 0.31]}
        ]
    }
    response = client.post("/infer/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data

def test_infer_voice():
    payload = {
        "frames": [
            {"landmark_0": [0.1, 0.2, 0.3]}
        ]
    }
    response = client.post("/infer/voice", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
