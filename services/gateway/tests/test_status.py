import httpx
from fastapi.testclient import TestClient

from app.main import app, get_http_client

client = TestClient(app)

def use_fake_services(handler):
    async def fake_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as fake:
            yield fake

    app.dependency_overrides[get_http_client] = fake_client


def teardown_function():
    app.dependency_overrides.clear() 
    # runs after every test, removes the fake so test dont affect each other

def test_status_ok_when_every_service_is_up():
    use_fake_services(lambda request: httpx.Response(200))
    body = client.get("/status").json()
    print(body)
    assert body["status"] == "ok"
    assert set(body["services"].values()) == {"up"}


def test_status_degraded_when_one_service_errors():
    def handler(request):
        if request.url.host == "rag":
            return httpx.Response(500)
        return httpx.Response(200)
    use_fake_services(handler)
    body = client.get("/status").json()

    assert body["status"] == "degraded"
    assert body["services"]["rag"] == "down"
    assert body["services"]["ingestion"] == "up"


def test_status_degraded_when_a_service_is_unreachable():
    def handler(request):
        if request.url.host == "floorplans":
            raise httpx.ConnectError("Connection refused")
        return httpx.Response(200)
    use_fake_services(handler)
    body = client.get("/status").json()

    assert body["status"] == "degraded"
    assert body["services"]["floorplans"] == "down"
    assert body["services"]["rag"] == "up"