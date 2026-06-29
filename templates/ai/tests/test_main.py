from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "dependencies" in data

def test_api_info():
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "operational"
    assert "enginesSupported" in data
