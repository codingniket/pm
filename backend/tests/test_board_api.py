import os


def test_board_seeded(client) -> None:
    response = client.get("/api/board?username=user")
    assert response.status_code == 200
    payload = response.json()
    assert payload["boardId"] == "board-user"
    assert len(payload["columns"]) == 5
    assert len(payload["cards"]) == 8


def test_db_initializes(client) -> None:
    client.get("/api/board?username=user")
    db_path = os.environ.get("PM_DB_PATH")
    assert db_path is not None
    assert os.path.exists(db_path)


def test_list_columns(client) -> None:
    response = client.get("/api/columns?username=user")
    assert response.status_code == 200
    columns = response.json()["columns"]
    assert len(columns) == 5
    assert columns[0]["title"] == "Backlog"


def test_list_cards(client) -> None:
    response = client.get("/api/cards?username=user")
    assert response.status_code == 200
    cards = response.json()["cards"]
    assert len(cards) == 8


def test_column_crud(client) -> None:
    create = client.post(
        "/api/columns",
        json={"username": "user", "title": "New Column"},
    )
    assert create.status_code == 200
    column_id = create.json()["id"]

    update = client.patch(
        f"/api/columns/{column_id}",
        json={"title": "Renamed Column"},
    )
    assert update.status_code == 200

    columns = client.get("/api/columns?username=user").json()["columns"]
    assert any(column["title"] == "Renamed Column" for column in columns)

    delete = client.delete(f"/api/columns/{column_id}")
    assert delete.status_code == 200


def test_card_crud(client) -> None:
    create = client.post(
        "/api/cards",
        json={
            "username": "user",
            "column_id": "col-backlog",
            "title": "Test card",
            "details": "Details",
        },
    )
    assert create.status_code == 200
    card_id = create.json()["id"]

    update = client.patch(
        f"/api/cards/{card_id}",
        json={"title": "Updated", "column_id": "col-review"},
    )
    assert update.status_code == 200

    board = client.get("/api/board?username=user").json()
    assert any(card["title"] == "Updated" for card in board["cards"].values())

    delete = client.delete(f"/api/cards/{card_id}")
    assert delete.status_code == 200
