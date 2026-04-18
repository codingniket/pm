# Frontend overview

This document describes the current Next.js frontend implementation, its structure, and how it is tested.

## Summary

- Next.js app router renders a single Kanban board at /.
- Board state loads from the backend API and persists changes.
- AI sidebar calls the backend to apply structured updates.
- Drag and drop uses dnd-kit; styling uses Tailwind CSS v4 with CSS variables.

## Tech stack

- Next.js 16 app router with React 19.
- dnd-kit for drag and drop.
- Tailwind CSS v4 via PostCSS.
- Vitest + Testing Library for unit tests.
- Playwright for E2E tests.

## Structure

- Root app entry: [frontend/src/app/page.tsx](frontend/src/app/page.tsx)
- Global styles and design tokens: [frontend/src/app/globals.css](frontend/src/app/globals.css)
- Kanban components: [frontend/src/components](frontend/src/components)
- AI chat sidebar: [frontend/src/components/AiSidebar.tsx](frontend/src/components/AiSidebar.tsx)
- Board data model and helpers: [frontend/src/lib/kanban.ts](frontend/src/lib/kanban.ts)

## Core UI components

- `KanbanBoard` owns board state, drag handling, and high-level layout. [frontend/src/components/KanbanBoard.tsx](frontend/src/components/KanbanBoard.tsx)
- `KanbanColumn` renders a column, title input, cards list, and add-card control. [frontend/src/components/KanbanColumn.tsx](frontend/src/components/KanbanColumn.tsx)
- `KanbanCard` renders a draggable card with delete button. [frontend/src/components/KanbanCard.tsx](frontend/src/components/KanbanCard.tsx)
- `KanbanCardPreview` renders the drag overlay preview. [frontend/src/components/KanbanCardPreview.tsx](frontend/src/components/KanbanCardPreview.tsx)
- `NewCardForm` handles add-card UI state. [frontend/src/components/NewCardForm.tsx](frontend/src/components/NewCardForm.tsx)

## Data model and behavior

- The board uses `BoardData` with `columns` and a `cards` map. [frontend/src/lib/kanban.ts](frontend/src/lib/kanban.ts)
- `initialData` seeds five columns with demo cards.
- `moveCard` handles reordering within a column and moving across columns.
- `createId` generates client-side ids for new cards.

## Styling and design system

- Design tokens are CSS variables in [frontend/src/app/globals.css](frontend/src/app/globals.css).
- Typography uses `font-display` and `font-body` CSS vars with Segoe UI fallbacks.
- Layout includes large radial gradients and card-like surfaces.

## Tests

Unit tests cover `KanbanBoard` behavior and `moveCard` logic. [frontend/src/components/KanbanBoard.test.tsx](frontend/src/components/KanbanBoard.test.tsx) and [frontend/src/lib/kanban.test.ts](frontend/src/lib/kanban.test.ts)
E2E tests are configured in [frontend/playwright.config.ts](frontend/playwright.config.ts).

## Scripts

Dev, build, and test scripts are defined in [frontend/package.json](frontend/package.json).
Unit tests run with `npm run test:unit`.
E2E tests run with `npm run test:e2e`.

## Conventions and notes

- `KanbanBoard` is a client component and owns all local state.
- Backend integration uses /api/board, /api/columns, and /api/cards for persistence.
- Auth is still local only; the frontend uses the demo "user" identity for API calls.
