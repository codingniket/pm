# Database schema

This schema supports a single board per user for the MVP while keeping tables flexible for future multi-board support.

## Tables

- users: login identity (username is unique)
- boards: one board per user for now
- columns: fixed columns per board, ordered by position
- cards: cards belong to a board and a column, ordered by position

## Keys and ordering

- All ids are text to keep UUIDs or short ids simple.
- Columns and cards use a zero-based integer position for ordering within their parent list.

## MVP assumptions

- A user has exactly one board; the backend should create it on first access.
- Column order is stable and can be renamed but not deleted in the MVP.
- Card order is per column and updated after drag-and-drop.

## Source of truth

- The schema definition lives in docs/db-schema.json and is used to guide backend implementation.
