import pytest

from backend import main


def test_ai_health_calls_azure_openai(client, monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyResponse:
        status_code = 200
        text = ""

        def json(self):
            return {"choices": [{"message": {"content": "4"}}]}

    def fake_post(url, headers=None, json=None):
        return DummyResponse()

    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    monkeypatch.setattr(main, "ai_post", fake_post)

    response = client.get("/api/ai/health")
    assert response.status_code == 200
    assert response.json()["reply"] == "4"
