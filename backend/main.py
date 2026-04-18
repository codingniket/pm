from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

app = FastAPI()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_OUT_DIR = PROJECT_ROOT / "frontend" / "out"


def load_project_env() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if (
            len(value) >= 2
            and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"))
        ):
            value = value[1:-1]

        os.environ.setdefault(key, value)


load_project_env()


def get_db_path() -> Path:
    env_path = os.getenv("PM_DB_PATH")
    if env_path:
        return Path(env_path)
    return PROJECT_ROOT / "backend" / "data" / "pm.db"


def get_db_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def init_db() -> None:
    with get_db_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS boards (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS columns (
                id TEXT PRIMARY KEY,
                board_id TEXT NOT NULL,
                title TEXT NOT NULL,
                position INTEGER NOT NULL,
                FOREIGN KEY (board_id) REFERENCES boards(id)
            );

            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                board_id TEXT NOT NULL,
                column_id TEXT NOT NULL,
                title TEXT NOT NULL,
                details TEXT NOT NULL,
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (board_id) REFERENCES boards(id),
                FOREIGN KEY (column_id) REFERENCES columns(id)
            );
            """
        )


def ensure_user_and_board(username: str) -> str:
    user_id = username
    board_id = f"board-{username}"
    created_at = now_iso()
    with get_db_connection() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO users (id, username, created_at) VALUES (?, ?, ?)",
            (user_id, username, created_at),
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO boards (id, user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (board_id, user_id, "Kanban Board", created_at, created_at),
        )
    ensure_seed_board(board_id)
    return board_id


def ensure_seed_board(board_id: str) -> None:
    with get_db_connection() as connection:
        existing = connection.execute(
            "SELECT COUNT(*) AS count FROM columns WHERE board_id = ?",
            (board_id,),
        ).fetchone()
        if existing and existing["count"] > 0:
            return

        seed_columns = [
            ("col-backlog", "Backlog"),
            ("col-discovery", "Discovery"),
            ("col-progress", "In Progress"),
            ("col-review", "Review"),
            ("col-done", "Done"),
        ]
        for index, (column_id, title) in enumerate(seed_columns):
            connection.execute(
                "INSERT INTO columns (id, board_id, title, position) VALUES (?, ?, ?, ?)",
                (column_id, board_id, title, index),
            )

        seed_cards = [
            ("card-1", "col-backlog", "Align roadmap themes", "Draft quarterly themes with impact statements and metrics."),
            ("card-2", "col-backlog", "Gather customer signals", "Review support tags, sales notes, and churn feedback."),
            ("card-3", "col-discovery", "Prototype analytics view", "Sketch initial dashboard layout and key drill-downs."),
            ("card-4", "col-progress", "Refine status language", "Standardize column labels and tone across the board."),
            ("card-5", "col-progress", "Design card layout", "Add hierarchy and spacing for scanning dense lists."),
            ("card-6", "col-review", "QA micro-interactions", "Verify hover, focus, and loading states."),
            ("card-7", "col-done", "Ship marketing page", "Final copy approved and asset pack delivered."),
            ("card-8", "col-done", "Close onboarding sprint", "Document release notes and share internally."),
        ]
        timestamp = now_iso()
        per_column_position: dict[str, int] = {}
        for card_id, column_id, title, details in seed_cards:
            position = per_column_position.get(column_id, 0)
            per_column_position[column_id] = position + 1
            connection.execute(
                """
                INSERT INTO cards (id, board_id, column_id, title, details, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (card_id, board_id, column_id, title, details, position, timestamp, timestamp),
            )


def fetch_board(board_id: str) -> dict[str, Any]:
    with get_db_connection() as connection:
        columns_rows = connection.execute(
            "SELECT id, title FROM columns WHERE board_id = ? ORDER BY position",
            (board_id,),
        ).fetchall()
        cards_rows = connection.execute(
            """
            SELECT id, title, details, column_id
            FROM cards
            WHERE board_id = ?
            ORDER BY column_id, position
            """,
            (board_id,),
        ).fetchall()

    cards: dict[str, dict[str, str]] = {}
    card_ids_by_column: dict[str, list[str]] = {row["id"]: [] for row in columns_rows}

    for row in cards_rows:
        cards[row["id"]] = {
            "id": row["id"],
            "title": row["title"],
            "details": row["details"],
        }
        card_ids_by_column.setdefault(row["column_id"], []).append(row["id"])

    columns = [
        {
            "id": row["id"],
            "title": row["title"],
            "cardIds": card_ids_by_column.get(row["id"], []),
        }
        for row in columns_rows
    ]
    return {"boardId": board_id, "columns": columns, "cards": cards}


def column_exists(connection: sqlite3.Connection, board_id: str, column_id: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM columns WHERE id = ? AND board_id = ?",
        (column_id, board_id),
    ).fetchone()
    return row is not None


def next_position(connection: sqlite3.Connection, table: str, board_id: str, column_id: str | None = None) -> int:
    if table == "columns":
        row = connection.execute(
            "SELECT COALESCE(MAX(position), -1) AS pos FROM columns WHERE board_id = ?",
            (board_id,),
        ).fetchone()
    else:
        row = connection.execute(
            """
            SELECT COALESCE(MAX(position), -1) AS pos
            FROM cards
            WHERE board_id = ? AND column_id = ?
            """,
            (board_id, column_id),
        ).fetchone()
    return int(row["pos"]) + 1


def get_ai_endpoint() -> str:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    if not endpoint:
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI is not configured. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY.",
        )
    return endpoint.rstrip("/")


def get_ai_api_key() -> str:
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI is not configured. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY.",
        )
    return api_key


def get_ai_api_version() -> str:
    return os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21").strip() or "2024-10-21"


def get_ai_model() -> str:
    return os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini").strip() or "gpt-4o-mini"


def get_chat_completions_url() -> str:
    explicit_url = os.getenv("AZURE_OPENAI_CHAT_COMPLETIONS_URL", "").strip()
    if explicit_url:
        return explicit_url

    endpoint = get_ai_endpoint()
    deployment = get_ai_model()
    api_version = get_ai_api_version()
    return f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"


def extract_ai_content(data: Any) -> str:
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Invalid Azure OpenAI response")

    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise HTTPException(status_code=502, detail="Invalid Azure OpenAI response")

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise HTTPException(status_code=502, detail="Invalid Azure OpenAI response")

    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise HTTPException(status_code=502, detail="Invalid Azure OpenAI response")

    content = message.get("content")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text" and isinstance(item.get("text"), str):
                text_parts.append(item["text"])
        if text_parts:
            return "\n".join(text_parts)

    raise HTTPException(status_code=502, detail="Invalid Azure OpenAI response")


def call_ai(prompt: str) -> str:
    return call_ai_messages([{"role": "user", "content": prompt}])


def call_ai_messages(messages: list[dict[str, str]]) -> str:
    payload = {"messages": messages, "temperature": 0}

    try:
        response = ai_post(
            get_chat_completions_url(),
            headers={"Content-Type": "application/json", "api-key": get_ai_api_key()},
            json=payload,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to reach Azure OpenAI endpoint.",
        ) from exc

    if response.status_code >= 400:
        detail = response.text.strip()[:220] if response.text else "no body"
        raise HTTPException(
            status_code=502,
            detail=f"Azure OpenAI call failed: {response.status_code} {detail}",
        )

    return extract_ai_content(response.json())


class ColumnCreate(BaseModel):
    username: str = "user"
    title: str
    position: int | None = None


class ColumnUpdate(BaseModel):
    title: str | None = None
    position: int | None = None


class CardCreate(BaseModel):
    username: str = "user"
    column_id: str
    title: str
    details: str = "No details yet."
    position: int | None = None


class CardUpdate(BaseModel):
    title: str | None = None
    details: str | None = None
    column_id: str | None = None
    position: int | None = None


class AiMessage(BaseModel):
    role: str
    content: str


class AiRequest(BaseModel):
    username: str = "user"
    question: str
    history: list[AiMessage] = []


class ColumnRename(BaseModel):
    column_id: str
    title: str


class CardCreateOp(BaseModel):
    column_id: str
    title: str
    details: str | None = None
    position: int | None = None


class CardUpdateOp(BaseModel):
    card_id: str
    title: str | None = None
    details: str | None = None


class CardMoveOp(BaseModel):
    card_id: str
    column_id: str
    position: int | None = None


class CardDeleteOp(BaseModel):
    card_id: str


class BoardUpdates(BaseModel):
    rename_columns: list[ColumnRename] = []
    create_cards: list[CardCreateOp] = []
    update_cards: list[CardUpdateOp] = []
    move_cards: list[CardMoveOp] = []
    delete_cards: list[CardDeleteOp] = []


class AiStructuredResponse(BaseModel):
    reply: str
    updates: BoardUpdates | None = None


def ai_post(url: str, headers: dict[str, str], json: dict[str, Any]) -> httpx.Response:
    with httpx.Client(timeout=20) as client:
        return client.post(url, headers=headers, json=json)


def load_fallback_html() -> str:
    html_path = Path(__file__).parent / "static" / "index.html"
    return html_path.read_text(encoding="utf-8")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/hello")
def hello() -> JSONResponse:
    return JSONResponse({"message": "Hello from FastAPI"})


@app.get("/api/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/api/ai/health")
def ai_health() -> JSONResponse:
    reply = call_ai("What is 2 + 2? Respond with only the number.")
    return JSONResponse({"reply": reply.strip()})


@app.get("/api/board")
def get_board(username: str = "user") -> JSONResponse:
    board_id = ensure_user_and_board(username)
    return JSONResponse(fetch_board(board_id))


@app.get("/api/columns")
def list_columns(username: str = "user") -> JSONResponse:
    board_id = ensure_user_and_board(username)
    with get_db_connection() as connection:
        rows = connection.execute(
            "SELECT id, title, position FROM columns WHERE board_id = ? ORDER BY position",
            (board_id,),
        ).fetchall()
    return JSONResponse(
        {
            "columns": [
                {"id": row["id"], "title": row["title"], "position": row["position"]}
                for row in rows
            ]
        }
    )


@app.post("/api/columns")
def create_column(payload: ColumnCreate) -> JSONResponse:
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is required")

    board_id = ensure_user_and_board(payload.username)
    column_id = f"col-{uuid4().hex[:10]}"
    with get_db_connection() as connection:
        position = payload.position
        if position is None:
            position = next_position(connection, "columns", board_id)
        connection.execute(
            "INSERT INTO columns (id, board_id, title, position) VALUES (?, ?, ?, ?)",
            (column_id, board_id, payload.title.strip(), position),
        )
    return JSONResponse({"id": column_id, "title": payload.title.strip(), "position": position})


@app.patch("/api/columns/{column_id}")
def update_column(column_id: str, payload: ColumnUpdate) -> JSONResponse:
    if payload.title is None and payload.position is None:
        raise HTTPException(status_code=400, detail="no updates provided")

    updates: list[str] = []
    values: list[Any] = []

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="title is required")
        updates.append("title = ?")
        values.append(title)
    if payload.position is not None:
        updates.append("position = ?")
        values.append(payload.position)

    values.append(column_id)

    with get_db_connection() as connection:
        result = connection.execute(
            f"UPDATE columns SET {', '.join(updates)} WHERE id = ?",
            values,
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="column not found")

    return JSONResponse({"status": "ok"})


@app.delete("/api/columns/{column_id}")
def delete_column(column_id: str) -> JSONResponse:
    with get_db_connection() as connection:
        connection.execute("DELETE FROM cards WHERE column_id = ?", (column_id,))
        result = connection.execute("DELETE FROM columns WHERE id = ?", (column_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="column not found")
    return JSONResponse({"status": "ok"})


@app.get("/api/cards")
def list_cards(username: str = "user") -> JSONResponse:
    board_id = ensure_user_and_board(username)
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, details, column_id, position
            FROM cards
            WHERE board_id = ?
            ORDER BY column_id, position
            """,
            (board_id,),
        ).fetchall()
    return JSONResponse(
        {
            "cards": [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "details": row["details"],
                    "columnId": row["column_id"],
                    "position": row["position"],
                }
                for row in rows
            ]
        }
    )


@app.post("/api/cards")
def create_card(payload: CardCreate) -> JSONResponse:
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    board_id = ensure_user_and_board(payload.username)
    card_id = f"card-{uuid4().hex[:10]}"
    with get_db_connection() as connection:
        if not column_exists(connection, board_id, payload.column_id):
            raise HTTPException(status_code=404, detail="column not found")

        position = payload.position
        if position is None:
            position = next_position(connection, "cards", board_id, payload.column_id)
        timestamp = now_iso()
        connection.execute(
            """
            INSERT INTO cards (id, board_id, column_id, title, details, position, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                card_id,
                board_id,
                payload.column_id,
                title,
                payload.details or "No details yet.",
                position,
                timestamp,
                timestamp,
            ),
        )
    return JSONResponse(
        {
            "id": card_id,
            "columnId": payload.column_id,
            "title": title,
            "details": payload.details or "No details yet.",
            "position": position,
        }
    )


@app.patch("/api/cards/{card_id}")
def update_card(card_id: str, payload: CardUpdate) -> JSONResponse:
    if (
        payload.title is None
        and payload.details is None
        and payload.column_id is None
        and payload.position is None
    ):
        raise HTTPException(status_code=400, detail="no updates provided")

    updates: list[str] = []
    values: list[Any] = []
    next_column_id = payload.column_id

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="title is required")
        updates.append("title = ?")
        values.append(title)

    if payload.details is not None:
        updates.append("details = ?")
        values.append(payload.details)

    with get_db_connection() as connection:
        if next_column_id is not None:
            board_row = connection.execute(
                "SELECT board_id FROM cards WHERE id = ?",
                (card_id,),
            ).fetchone()
            if not board_row:
                raise HTTPException(status_code=404, detail="card not found")
            board_id = board_row["board_id"]
            if not column_exists(connection, board_id, next_column_id):
                raise HTTPException(status_code=404, detail="column not found")
            updates.append("column_id = ?")
            values.append(next_column_id)
            if payload.position is None:
                payload.position = next_position(connection, "cards", board_id, next_column_id)

        if payload.position is not None:
            updates.append("position = ?")
            values.append(payload.position)

        updates.append("updated_at = ?")
        values.append(now_iso())

        values.append(card_id)
        result = connection.execute(
            f"UPDATE cards SET {', '.join(updates)} WHERE id = ?",
            values,
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="card not found")

    return JSONResponse({"status": "ok"})


@app.delete("/api/cards/{card_id}")
def delete_card(card_id: str) -> JSONResponse:
    with get_db_connection() as connection:
        result = connection.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="card not found")
    return JSONResponse({"status": "ok"})


def apply_updates(board_id: str, updates: BoardUpdates) -> None:
    with get_db_connection() as connection:
        connection.execute("BEGIN")

        for rename in updates.rename_columns:
            title = rename.title.strip()
            if not title:
                raise HTTPException(status_code=400, detail="column title is required")
            if not column_exists(connection, board_id, rename.column_id):
                raise HTTPException(status_code=400, detail="column not found")

        for card in updates.update_cards:
            row = connection.execute(
                "SELECT 1 FROM cards WHERE id = ? AND board_id = ?",
                (card.card_id, board_id),
            ).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="card not found")

        for move in updates.move_cards:
            row = connection.execute(
                "SELECT 1 FROM cards WHERE id = ? AND board_id = ?",
                (move.card_id, board_id),
            ).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="card not found")
            if not column_exists(connection, board_id, move.column_id):
                raise HTTPException(status_code=400, detail="column not found")

        for create in updates.create_cards:
            if not create.title.strip():
                raise HTTPException(status_code=400, detail="card title is required")
            if not column_exists(connection, board_id, create.column_id):
                raise HTTPException(status_code=400, detail="column not found")

        for delete in updates.delete_cards:
            row = connection.execute(
                "SELECT 1 FROM cards WHERE id = ? AND board_id = ?",
                (delete.card_id, board_id),
            ).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="card not found")

        for rename in updates.rename_columns:
            connection.execute(
                "UPDATE columns SET title = ? WHERE id = ? AND board_id = ?",
                (rename.title.strip(), rename.column_id, board_id),
            )

        for create in updates.create_cards:
            card_id = f"card-{uuid4().hex[:10]}"
            position = create.position
            if position is None:
                position = next_position(connection, "cards", board_id, create.column_id)
            timestamp = now_iso()
            connection.execute(
                """
                INSERT INTO cards (id, board_id, column_id, title, details, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    card_id,
                    board_id,
                    create.column_id,
                    create.title.strip(),
                    (create.details or "No details yet."),
                    position,
                    timestamp,
                    timestamp,
                ),
            )

        for card in updates.update_cards:
            updates_sql: list[str] = []
            values: list[Any] = []
            if card.title is not None:
                title = card.title.strip()
                if not title:
                    raise HTTPException(status_code=400, detail="card title is required")
                updates_sql.append("title = ?")
                values.append(title)
            if card.details is not None:
                updates_sql.append("details = ?")
                values.append(card.details)
            if updates_sql:
                updates_sql.append("updated_at = ?")
                values.append(now_iso())
                values.append(card.card_id)
                connection.execute(
                    f"UPDATE cards SET {', '.join(updates_sql)} WHERE id = ?",
                    values,
                )

        for move in updates.move_cards:
            position = move.position
            if position is None:
                position = next_position(connection, "cards", board_id, move.column_id)
            connection.execute(
                "UPDATE cards SET column_id = ?, position = ?, updated_at = ? WHERE id = ?",
                (move.column_id, position, now_iso(), move.card_id),
            )

        for delete in updates.delete_cards:
            connection.execute("DELETE FROM cards WHERE id = ?", (delete.card_id,))


@app.post("/api/ai/query")
def ai_query(payload: AiRequest) -> JSONResponse:
    board_id = ensure_user_and_board(payload.username)
    board_state = fetch_board(board_id)

    system_prompt = (
        "You are a project management assistant. "
        "Return JSON that matches this schema: "
        "{reply: string, updates: {rename_columns: [{column_id, title}], "
        "create_cards: [{column_id, title, details?, position?}], "
        "update_cards: [{card_id, title?, details?}], "
        "move_cards: [{card_id, column_id, position?}], "
        "delete_cards: [{card_id}]}}. "
        "Use empty arrays for no updates. Return JSON only."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        *[{"role": msg.role, "content": msg.content} for msg in payload.history],
        {
            "role": "user",
            "content": (
                "Board state:\n"
                f"{json.dumps(board_state)}\n\n"
                "User question:\n"
                f"{payload.question}"
            ),
        },
    ]

    raw = call_ai_messages(messages)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return JSONResponse({"reply": raw.strip(), "applied": False, "board": board_state})

    try:
        structured = AiStructuredResponse.model_validate(parsed)
    except ValidationError:
        fallback_reply = "" if not isinstance(parsed, dict) else str(parsed.get("reply", ""))
        return JSONResponse({"reply": fallback_reply, "applied": False, "board": board_state})

    if structured.updates:
        apply_updates(board_id, structured.updates)

    return JSONResponse(
        {
            "reply": structured.reply,
            "applied": bool(structured.updates),
            "board": fetch_board(board_id),
        }
    )


if FRONTEND_OUT_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_OUT_DIR, html=True), name="frontend")
else:

    @app.get("/", response_class=HTMLResponse)
    def read_root() -> HTMLResponse:
        return HTMLResponse(load_fallback_html())
