import os
import tempfile
import uuid

os.environ["SQLITE_PATH"] = os.path.join(tempfile.gettempdir(), "scholr-router-tests.db")

from fastapi.testclient import TestClient

import main
from cache.response_cache import ResponseCache
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


def test_health_routes_lists_registered_api_paths():
    client = TestClient(main.app)

    response = client.get("/health/routes")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["routes"], list)
    assert body["total_routes"] > 5
    paths = {route["path"] for route in body["routes"]}
    assert "/api/metrics" in paths
    assert "/api/waitlist" in paths
    assert "/api/research" in paths


def test_metrics_route_returns_aggregate_keys():
    client = TestClient(main.app)

    response = client.get("/api/metrics")

    assert response.status_code == 200
    body = response.json()
    assert "searches" in body
    assert "feedback" in body
    assert "cache" in body
    assert {"total", "last_24h", "last_7d", "by_module"}.issubset(body["searches"].keys())


def test_response_cache_returns_none_for_unknown_key():
    cache = ResponseCache()

    assert cache.get("notes", "operating systems", "fast") is None


def test_response_cache_returns_cached_value():
    cache = ResponseCache()

    cache.set("notes", "operating systems", "fast", "cached notes")

    assert cache.get("notes", "operating systems", "fast") == "cached notes"


def test_response_cache_respects_ttl():
    cache = ResponseCache(ttl_seconds=0)

    cache.set("notes", "operating systems", "fast", "cached notes")

    assert cache.get("notes", "operating systems", "fast") is None


def test_waitlist_route_accepts_new_email():
    client = TestClient(main.app)
    email = f"student-new-{uuid.uuid4().hex}@example.com"

    response = client.post("/api/waitlist", json={"email": email})

    assert response.status_code == 200
    assert response.json()["added"] is True


def test_waitlist_route_reports_duplicate_email():
    client = TestClient(main.app)
    email = f"student-duplicate-{uuid.uuid4().hex}@example.com"

    first = client.post("/api/waitlist", json={"email": email})
    second = client.post("/api/waitlist", json={"email": email})

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["already_registered"] is True


def test_waitlist_route_rejects_invalid_email():
    client = TestClient(main.app)

    response = client.post("/api/waitlist", json={"email": "not-an-email"})

    assert response.status_code == 422


def test_validation_session_accepts_valid_payload():
    client = TestClient(main.app)

    response = client.post(
        "/api/validation/session",
        json={"college": "Test Engineering College", "year": "third_year", "referred_by": "pytest"},
    )

    assert response.status_code == 200
    assert response.json()["recorded"] is True


def test_validation_summary_returns_goal():
    client = TestClient(main.app)

    response = client.get("/api/validation/summary")

    assert response.status_code == 200
    body = response.json()
    assert "total_validation_sessions" in body
    assert body["validation_goal"] == 10


def test_evidence_route_returns_technical_package():
    client = TestClient(main.app)

    response = client.get("/api/evidence")

    assert response.status_code == 200
    body = response.json()
    assert {"product", "tech_stack", "engineering_features", "production_stats"}.issubset(body.keys())
    assert isinstance(body["engineering_features"], list)
    assert len(body["engineering_features"]) > 5
