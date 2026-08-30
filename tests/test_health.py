from fastapi.testclient import TestClient

from atlas.main import app

client = TestClient(app)


def test_liveness():
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "service": "atlas-api",
    }

    assert "X-Request-ID" in response.headers
