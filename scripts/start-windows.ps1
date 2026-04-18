$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Test-Path "frontend\node_modules")) {
	npm --prefix frontend install
}
npm --prefix frontend run build

uv run --project backend uvicorn backend.main:app --reload --port 8000
