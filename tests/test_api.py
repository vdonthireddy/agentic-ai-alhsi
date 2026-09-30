"""Unit tests for the FastAPI web server endpoints."""

from fastapi.testclient import TestClient
from alhsi.server.app import app

client = TestClient(app)


def test_api_presets():
    res = client.get("/api/presets")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3
    ids = [p["id"] for p in data]
    assert "nanogpt" in ids
    assert "matmul" in ids
    assert "reasoning" in ids


def test_api_state():
    res = client.get("/api/state")
    assert res.status_code == 200
    data = res.json()
    assert "phase" in data
    assert "baseline_metric" in data
    assert "trials" in data


def test_api_step():
    res = client.post("/api/step")
    assert res.status_code == 200
    trial = res.json()
    assert "trial_num" in trial
    assert "status" in trial
    assert "hypothesis" in trial


def test_api_reset():
    res = client.post("/api/reset", json={"preset_id": "matmul", "agent_type": "sim"})
    assert res.status_code == 200
    state = res.json()
    assert state["preset"]["id"] == "matmul"
    assert state["total_trials"] == 0
