from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)# fake browser that calls the app directly, no server needs to be running


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body ["status"]== "ok"
    assert body ["service"]== "gateway"
    assert body ["version"]== "0.1.0"