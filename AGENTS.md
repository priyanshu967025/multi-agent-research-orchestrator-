# AGENTS.md

Non-obvious learnings for future sessions. Read this before making changes.

## Provider / LLM Configuration

- Providers supported: `groq`, `gemini`, `openai`, `anthropic`, `ollama`.
- `gemini` uses `langchain_google_genai.ChatGoogleGenerativeAI` with `gemini-2.0-flash` default. Accepts `GEMINI_API_KEY` or `GOOGLE_API_KEY`.
- Agents must pass `model=None` to `get_llm_with_fallback()`. Passing `MODEL_NAME` overrides per-provider defaults.
- `config/setting.py`'s `MODEL_NAME` default (`llama-3.3-70b-versatile`) is correct for Groq. Do not change it to an OpenAI-style model name — it breaks auto-detection.
- `get_llm_with_fallback` re-imports all langchain provider modules inside the loop on every call. This is intentional — lazy imports avoid `ImportError` when a provider package isn't installed.
- Researcher node features intelligent DuckDuckGo search fallback (`duckduckgo_search.DDGS`) when Tavily API key is absent or exhausts rate limits.

## Project Structure

- `frontend/`: Modern React + Vite Single Page Application with real-time DAG graph visualizer, SSE streaming terminal, interactive RAG sandbox, benchmark arena, and multi-format report exporter.
- `backend/`: Django REST Framework backend with Token Auth, SSE streaming, RAG querying, session exports (`/api/research/sessions/<id>/export/?format=md|html|json|bibtex`), and platform analytics (`/api/stats/`).
- `config/providers.py`: Multi-provider abstraction with Groq, Gemini, OpenAI, Anthropic, Ollama.

## Testing

- Run tests from inside `backend/`: `cd backend && python -m pytest -q`.
- 62 tests total: `test_auth` (14), `test_benchmark` (10), `test_research` (14), `test_research_jobs` (6), `test_platform_features` (10), plus 8 streaming/tags tests. All 62 pass with 100% success rate.

## Content Negotiation & Export

- DRF format suffix negotiation intercepts `?format=...`. `ExportReportAPIView` implements custom `perform_content_negotiation` returning `JSONRenderer` for json and `PassthroughRenderer` for text/html/bibtex/markdown.


## MCP Server

- The MCP server's `research_topic` tool builds its own `initial_state` dict rather than using `services.initial_research_state()`. This keeps the MCP server independent of Django models and migrations.
- FastMCP server constructor uses `instructions=` (prompt text), not `description=`. `description` is for server metadata only.
- Authenticated MCP tools (sessions, tags) require `BACKEND_AUTH_TOKEN` env var. The token comes from Django login — set it after authenticating via the Streamlit UI.

## Windows-Specific

- PowerShell `Start-Process -RedirectStandardOutput` and `-RedirectStandardError` must point to **different files** or the process silently fails.
- Path with spaces (like `D:\GEN AI PROJECT CV\...`) breaks PowerShell redirection. Use a `.ps1` script file instead of inline `-Command`.
- `streamlit.exe` is at `.venv/Scripts/streamlit.exe`, not `streamlit` on PATH.
- **Streamlit socket crash (WinError 64):** `Start-Process` with `-WindowStyle Hidden` or `cmd.exe /c start` corrupts the asyncio socket on Windows. Use `pythonw.exe -m streamlit run ...` instead — it creates a proper background process without console detachment issues.
- Django dev server (`python manage.py runserver`) works fine with `Start-Process -WindowStyle Hidden` — only Streamlit's asyncio socket is affected.

## API URL Mapping

- `workspace_api.py` must match Django URL patterns exactly. Key mapping:
  - `create_job` → `POST /research/jobs/` (ResearchJobsAPIView)
  - `list_jobs` → `GET /research/jobs/` (ResearchJobsAPIView)
  - `get_job` → `GET /research/sessions/{id}/` (SessionDetailAPIView) — **NOT** `/research/jobs/{id}/`
  - `delete_job` → `DELETE /research/sessions/{id}/` (SessionDetailAPIView) — **NOT** `/research/jobs/{id}/`
  - Tags → `/research/{id}/tags/` (ResearchTagsAPIView)
  - Health → `/health/` (HealthAPIView) — required by Streamlit's API availability check.

## Tracked vs Untracked Files

- **Tracked (modified):** `agents/*.py`, `app.py`, `mcp_server.py`, `requirements.txt`, `.gitignore`, `README.md`, `config/setting.py` (reverted to original).
- **Untracked (new):** `backend/`, `app_pages/`, `workspace_api.py`, `config/providers.py`, `benchmark/evaluator.py`, `.env.example`, `.streamlit/config.toml`.
