# Backend overview

This document describes the current FastAPI backend scaffold.

## Summary

- FastAPI app serves a static HTML page at / and a JSON API for the Kanban board.
- API routes include /api/board, /api/columns, and /api/cards for board data and CRUD.
- Azure OpenAI connectivity check is exposed at /api/ai/health.
- Structured AI updates are handled by /api/ai/query.
- Backend uses SQLite for persistence and pytest for unit tests.

## Key files

- App entrypoint: [backend/main.py](backend/main.py)
- Static HTML page: [backend/static/index.html](backend/static/index.html)
- Tests: [backend/tests/test_api.py](backend/tests/test_api.py), [backend/tests/test_board_api.py](backend/tests/test_board_api.py), [backend/tests/test_ai_api.py](backend/tests/test_ai_api.py), [backend/tests/test_ai_structured.py](backend/tests/test_ai_structured.py)
- Python project config: [backend/pyproject.toml](backend/pyproject.toml)

## Behavior

- GET / returns a static HTML page that calls /api/hello via fetch.
- GET /api/hello returns {"message": "Hello from FastAPI"}.
- GET /api/health returns {"status": "ok"}.
- GET /api/board returns the board state for a user.
- CRUD routes for columns and cards are available under /api/columns and /api/cards.
- GET /api/ai/health calls Azure OpenAI with a simple prompt.
- POST /api/ai/query sends board state + question and applies structured updates.

## Scripts

- Start/stop scripts live in [scripts](scripts) and use uv + uvicorn on port 8000.
