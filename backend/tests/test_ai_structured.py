import pytest

from backend import main


def test_ai_query_applies_updates(client, monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyResponse:
        status_code = 200
        text = ""

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                "{\"reply\":\"Updated.\","
                                "\"updates\":{"
                                "\"rename_columns\":[{\"column_id\":\"col-backlog\",\"title\":\"Ideas\"}],"
                                "\"create_cards\":[{\"column_id\":\"col-review\",\"title\":\"New task\",\"details\":\"Check in\"}]"
                                "}}"
                            )
                        }
                    }
                ]
            }

    def fake_post(url, headers=None, json=None):
        return DummyResponse()

    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    monkeypatch.setattr(main, "ai_post", fake_post)

    response = client.post(
        "/api/ai/query",
        json={"username": "user", "question": "Update the board"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["reply"] == "Updated."
    assert payload["applied"] is True

    board = payload["board"]
    assert any(column["title"] == "Ideas" for column in board["columns"])
    assert any(card["title"] == "New task" for card in board["cards"].values())


def test_ai_query_invalid_json_no_updates(client, monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyResponse:
        status_code = 200
        text = ""

        def json(self):
            return {"choices": [{"message": {"content": "not-json"}}]}

    def fake_post(url, headers=None, json=None):
        return DummyResponse()

    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    monkeypatch.setattr(main, "ai_post", fake_post)

    before = client.get("/api/board?username=user").json()
    response = client.post(
        "/api/ai/query",
        json={"username": "user", "question": "Bad response"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["applied"] is False

    after = payload["board"]
    assert before["columns"] == after["columns"]
    assert before["cards"].keys() == after["cards"].keys()
