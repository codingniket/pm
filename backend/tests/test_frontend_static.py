from pathlib import Path

import pytest
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_OUT_DIR = PROJECT_ROOT / "frontend" / "out"


@pytest.mark.skipif(not FRONTEND_OUT_DIR.exists(), reason="frontend build output missing")
def test_frontend_static_is_served(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
