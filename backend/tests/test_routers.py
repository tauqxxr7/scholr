import os
import tempfile

os.environ["SQLITE_PATH"] = os.path.join(tempfile.gettempdir(), "scholr-router-tests.db")

from fastapi.testclient import TestClient

import main
from routers import doubt as doubt_router
from routers import notes as notes_router
from routers import research as research_router


async def _fake_stream(*args, **kwargs):
    del args, kwargs
    yield "mocked academic response"


def _disable_provider_fallback(monkeypatch):
    monkeypatch.setattr(research_router, "generate_research_response", _fake_stream)
    monkeypatch.setattr(notes_router, "generate_notes_response", _fake_stream)
    monkeypatch.setattr(doubt_router, "generate_doubt_response", _fake_stream)
    monkeypatch.setattr(research_router, "should_use_emergency_fallback", lambda: False)
    monkeypatch.setattr(notes_router, "should_use_emergency_fallback", lambda: False)
    monkeypatch.setattr(doubt_router, "should_use_emergency_fallback", lambda: False)


def test_research_route_returns_event_stream(monkeypatch):
    _disable_provider_fallback(monkeypatch)
    client = TestClient(main.app)

    response = client.post("/api/research", json={"topic": "binary search trees"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


def test_notes_route_returns_event_stream(monkeypatch):
    _disable_provider_fallback(monkeypatch)
    client = TestClient(main.app)

    response = client.post("/api/notes", json={"topic": "operating systems"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


def test_doubt_route_returns_event_stream(monkeypatch):
    _disable_provider_fallback(monkeypatch)
    client = TestClient(main.app)

    response = client.post("/api/doubt", json={"question": "what is normalization"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


def test_feedback_route_accepts_valid_payload():
    client = TestClient(main.app)

    response = client.post(
        "/api/feedback",
        json={
            "module": "notes",
            "query": "operating systems",
            "rating": "helpful",
            "response_length": 128,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"received": True}


def test_history_route_returns_ok():
    client = TestClient(main.app)

    response = client.get("/api/history")

    assert response.status_code == 200


def test_health_route_returns_status_key():
    client = TestClient(main.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert "status" in response.json()


def test_metrics_route_returns_aggregate_keys():
    client = TestClient(main.app)

    response = client.get("/api/metrics")

    assert response.status_code == 200
    body = response.json()
    assert "searches" in body
    assert "feedback" in body
    assert {"total", "last_24h", "last_7d", "by_module"}.issubset(body["searches"].keys())
