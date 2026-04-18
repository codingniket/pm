#!/usr/bin/env sh
set -e

project_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$project_root"

if [ ! -d "frontend/node_modules" ]; then
	npm --prefix frontend install
fi
npm --prefix frontend run build

uv run --project backend uvicorn backend.main:app --reload --port 8000
