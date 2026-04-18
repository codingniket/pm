# Project plan

This document expands the implementation plan into actionable checklists, tests, and success criteria. Each part must be completed and approved before moving to the next.

## Part 1: Plan

Goal: Produce a detailed plan and document the existing frontend.

Checklist:

- [ ] Review requirements in AGENTS.md and note conflicts. Azure OpenAI requirements are the source of truth.
- [ ] Replace this PLAN.md with detailed checklists, tests, and success criteria for Parts 1-10.
- [ ] Verify backend/AGENTS.md and frontend/AGENTS.md reflect the current code and tests.
- [ ] Ask for user approval before starting Part 2.

Tests:

- [ ] Manual review of docs for completeness and consistency.

Success criteria:

- The plan is detailed, actionable, and aligned with AGENTS.md.
- frontend/AGENTS.md accurately describes the existing frontend.
- backend/AGENTS.md accurately describes the existing backend scaffold.
- User approval is recorded before any implementation work.

## Part 2: Scaffolding

Goal: Scaffold the backend and scripts; verify a simple HTML page and API call locally.

Checklist:

- [ ] Ensure FastAPI app in backend/ has a health route and a simple API route.
- [ ] Serve a static HTML page at / that calls the API route (fetch) and shows a response.
- [ ] Document how to run locally in a concise docs entry (scripts, ports, expected output).
- [ ] Add a short note describing uv usage for local runs.

Tests:

- [ ] Backend unit test for the API route.
- [ ] Manual run: open / and confirm HTML renders and API response appears.

Success criteria:

- Local run shows static HTML and a successful API call.
- Local run instructions are present and correct.

## Part 3: Add in frontend

Goal: Build and serve the existing Next.js frontend statically at /.

Checklist:

- [ ] Update backend to serve the built frontend assets at /.
- [ ] Ensure routing serves the Kanban board on the root path.
- [ ] Update build/start scripts to build the frontend and serve it from the backend.
- [ ] Document the frontend build output location and how it is served.

Tests:

- [ ] Unit tests for frontend components (existing vitest suite).
- [ ] Integration test confirming the built frontend renders at /.

Success criteria:

- / displays the Kanban board from the built frontend.
- Unit and integration tests pass.

## Part 4: Fake user sign-in

Goal: Require a simple login before viewing the Kanban board.

Checklist:

- [ ] Add login UI for username/password on /.
- [ ] Hardcode acceptance of user/password only.
- [ ] Add logout control and session reset.
- [ ] Prevent board rendering until login is complete.

Tests:

- [ ] Unit test for login form behavior.
- [ ] Integration test: unauthorized users see login; authorized users see board; logout returns to login.

Success criteria:

- Login gate is enforced and stable.
- Tests pass for sign-in/out flow.

## Part 5: Database modeling

Goal: Define and document a database schema for boards, columns, and cards.

Checklist:

- [ ] Propose a schema as JSON (tables, fields, types, relationships).
- [ ] Store the JSON schema under docs/.
- [ ] Document the approach and assumptions in docs/.
- [ ] Get user sign-off before implementing any database code.

Tests:

- [ ] Manual review of schema for completeness and alignment with features.

Success criteria:

- Schema JSON exists and is clear.
- Documentation explains mapping from UI to data model.
- User approval recorded.

## Part 6: Backend

Goal: Implement API routes for reading and modifying the Kanban board per user.

Checklist:

- [ ] Create SQLite database if it does not exist.
- [ ] Add CRUD routes for columns scoped to a user.
- [ ] Add CRUD routes for cards scoped to a user.
- [ ] Add route to fetch board state for a user.
- [ ] Ensure validation and simple error handling for bad input.

Tests:

- [ ] Backend unit tests for all routes.
- [ ] Database initialization test (create-on-missing).

Success criteria:

- Backend can read and update the board for a user.
- All backend tests pass.

## Part 7: Frontend + backend

Goal: Wire the frontend to the backend API for persistence.

Checklist:

- [ ] Replace in-memory board state with API-driven state.
- [ ] Persist updates when renaming columns, adding/removing cards, and moving cards.
- [ ] Handle loading and error states simply.
- [ ] Keep UI responsive while requests are in flight.

Tests:

- [ ] Integration tests for CRUD flows with the backend.
- [ ] E2E test: login, edit board, refresh, changes persist.

Success criteria:

- Board changes persist across refresh.
- All tests pass.

## Part 8: AI connectivity

Goal: Prove Azure OpenAI connectivity with a simple test.

Checklist:

- [ ] Use Azure OpenAI config from .env (endpoint, key, api version, deployment).
- [ ] Add backend route or test utility that calls the model `gpt-4o-mini`.
- [ ] Implement a simple "2+2" prompt and capture the response.
- [ ] Return a minimal response payload suitable for a health check.

Tests:

- [ ] Integration test for the AI connectivity route.

Success criteria:

- Backend successfully calls Azure OpenAI and returns a valid response.

## Part 9: Structured outputs

Goal: Send board state + user question to the model and parse structured responses.

Checklist:

- [ ] Define a structured output schema with response text and optional board updates.
- [ ] Send board JSON + question + conversation history to the model.
- [ ] Validate and apply structured updates safely.
- [ ] Ensure no updates are applied when validation fails.

Tests:

- [ ] Unit tests for schema validation and update application.
- [ ] Integration test for a response that updates the board.

Success criteria:

- Structured responses are parsed reliably.
- Optional board updates are applied correctly.

## Part 10: AI sidebar UI

Goal: Add an AI chat sidebar that can update the Kanban based on structured outputs.

Checklist:

- [ ] Build sidebar chat UI with history and input.
- [ ] Wire to backend AI route.
- [ ] Apply board updates from structured outputs and refresh UI state.
- [ ] Support simple error display and retry.

Tests:

- [ ] UI tests for chat flow and update rendering.
- [ ] E2E test: ask AI to add/move a card and verify board update.

Success criteria:

- Chat is functional and usable.
- Board updates reflect AI responses without manual refresh.
