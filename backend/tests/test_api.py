def test_hello_api(client) -> None:
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI"}


def test_health_api(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_html(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
