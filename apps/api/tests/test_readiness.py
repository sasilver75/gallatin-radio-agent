from fastapi.testclient import TestClient

from gallatin_api.main import create_app
from gallatin_api.readiness import DependencyStatus


def test_healthz_reports_process_liveness() -> None:
    client = TestClient(create_app())

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "service": "gallatin-radio-agent-api",
        "status": "ok",
    }


def test_readyz_reports_postgis_ready() -> None:
    def ready_postgis(_: str) -> DependencyStatus:
        return DependencyStatus(
            name="postgis",
            status="ready",
            details="POSTGIS='3.4.0'",
        )

    client = TestClient(create_app(readiness_checker=ready_postgis))

    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {
        "service": "gallatin-radio-agent-api",
        "status": "ready",
        "dependencies": [
            {
                "name": "postgis",
                "status": "ready",
                "details": "POSTGIS='3.4.0'",
            }
        ],
    }


def test_readyz_fails_clearly_when_postgis_is_unavailable() -> None:
    def unavailable_postgis(_: str) -> DependencyStatus:
        return DependencyStatus(
            name="postgis",
            status="unavailable",
            details="PostGIS readiness check failed: OperationalError: connection refused",
        )

    client = TestClient(create_app(readiness_checker=unavailable_postgis))

    response = client.get("/readyz")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["dependencies"][0]["name"] == "postgis"
    assert body["dependencies"][0]["status"] == "unavailable"
    assert "connection refused" in body["dependencies"][0]["details"]
