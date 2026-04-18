# Local run

These steps run the backend and serve either the static fallback page or the built frontend.

## Prerequisites

- Node.js 20+ for the frontend build
- Python 3.11+
- uv installed (Python package manager used by scripts)
- Azure OpenAI credentials in `.env`

## Windows

1. Run the start script:

   ```powershell
   .\scripts\start-windows.ps1
   ```

2. Open http://localhost:8000

## Notes

- The start script builds the frontend and runs FastAPI via uvicorn on port 8000.
- The frontend build output is written to frontend/out.
- If the frontend build output exists, it is served at /.
- Otherwise, the backend serves the fallback HTML page at /.
- Use uv locally to match the Docker environment.
- AI endpoints use Azure OpenAI-compatible chat or responses routes derived from `.env`.
- Required env vars: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`.
- Optional env vars: `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_CHAT_COMPLETIONS_URL`, `AZURE_OPENAI_RESPONSES_URL`.
