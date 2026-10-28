def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["ml_mode"] == "mock"
    assert data["models_loaded"] is True
    assert data["database_status"] == "connected"
    assert "informational and is not legal advice" in data["disclaimer"]


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "ClauseGuard" in data["message"]
    assert "informational" in data["disclaimer"]
