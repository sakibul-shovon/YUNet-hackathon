from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_live():
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "claimcraft-bd"
    assert "environment" in data


def test_health_ready():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "capabilities" in data


def test_api_ping():
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
