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
