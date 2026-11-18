import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.database import Base, get_db


@pytest.fixture
def client(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=test_engine, autoflush=False, autocommit=False
    )
    Base.metadata.create_all(bind=test_engine)
    monkeypatch.setattr(main, "engine", test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()
    test_engine.dispose()


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_seed_and_metrics(client):
    seeded = client.post("/api/demo/seed")
    assert seeded.status_code == 200
    assert seeded.json()["created"] == 4

    metrics = client.get("/api/metrics").json()
    assert metrics["requests"] == 4
    assert metrics["failures"] == 1
    assert metrics["error_rate"] == 0.25


def test_trace_can_be_created_and_retrieved(client):
    created = client.post(
        "/api/traces",
        json={
            "prompt": "Explain a database index",
            "response": "It helps look up rows faster.",
            "latency_ms": 125,
            "input_tokens": 20,
            "output_tokens": 12,
        },
    )
    assert created.status_code == 200
    trace_id = created.json()["trace_id"]

    fetched = client.get(f"/api/traces/{trace_id}")
    assert fetched.status_code == 200
    assert fetched.json()["prompt"] == "Explain a database index"


def test_evaluation_is_saved_and_listed(client):
    response = client.post(
        "/api/evaluations",
        json={
            "name": "smoke test",
            "metric": "exact_match",
            "cases": [
                {"input": "1", "actual": "yes", "expected": "yes"},
                {"input": "2", "actual": "no", "expected": "yes"},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["score"] == 0.5
    assert len(client.get("/api/evaluations").json()) == 1


def test_invalid_trace_status_is_rejected(client):
    response = client.post(
        "/api/traces",
        json={"prompt": "test", "status": "pending"},
    )
    assert response.status_code == 422


def test_unknown_trace_returns_404(client):
    response = client.get("/api/traces/does-not-exist")
    assert response.status_code == 404
