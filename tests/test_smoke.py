from fastapi.testclient import TestClient
from main import app

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_dashboard_loads():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "FinanSys" in response.text
