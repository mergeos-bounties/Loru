from fastapi.testclient import TestClient
from loru.api.app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_infer_text():
    response = client.post("/infer/text", json={"landmarks": [[0.0, 0.0]]})
    assert response.status_code == 200
    assert "text" in response.json()