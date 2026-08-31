# Full-Stack Research Workspace Design

## Objective

Evolve the Multi-Agent Research Orchestrator from a capable prototype into a coherent full-stack workspace. Users submit a research brief, follow a durable agent run, inspect evidence and quality results, export the finished report, and revisit their saved work.

## Scope

This milestone retains the existing LangGraph agents, Chroma RAG, Django REST API, Streamlit application, and MCP interface. It creates one primary browser flow through the Django API rather than allowing Streamlit to be a competing execution backend.

Included:

- Research-job lifecycle with queued, running, completed, and failed states.
- Progress events that expose agent stage, human-readable message, sequence number, and safe timestamp.
- Source/evidence records associated with completed research sessions.
- API endpoints to create a run, inspect its status, list user-owned runs, inspect reports, and delete a saved report.
- API-first Streamlit workspace for submission, progress, results, exports, and a report library.
- Validation, resource ownership, predictable failures, and automated tests.
- Documentation for local setup and the workspace API.

Not included:

- Distributed job queues, Celery, Redis, or automatic retries.
- WebSockets/server-sent events; the UI uses bounded polling.
- A separate React/Next.js application.
- Multi-tenant organization management, billing, or cloud deployment automation.

## Architecture

```text
Streamlit research workspace
        |
        | authenticated REST requests + status polling
        v
Django REST API and persistent SQLite data
        |
        | research execution service
        v
LangGraph: researcher -> analyst -> fact checker -> writer
        |                                      |
        v                                      v
Tavily + Chroma RAG                    report, progress, evidence
```

Django owns every job, event, source, report, and authorization decision. Streamlit only invokes and renders REST resources. The existing graph remains the domain pipeline. A small execution service converts graph state/messages into session transitions and persisted events; API views should not contain orchestration details.

## Data Model

`ResearchSession` is extended or replaced only through a forward migration and remains the root record. It stores topic, owner, status, started/completed timestamps, report, revision count, source counts, error code/message, and a monotonic progress version.

`ResearchEvent` belongs to a session and stores a sequence number, stage (`queued`, `researcher`, `analyst`, `fact_checker`, `writer`, `completed`, `failed`), user-safe message, and timestamp. The sequence is unique per session to preserve display order.

`ResearchSource` belongs to a session and stores a validated URL, title/domain where available, bounded snippet, source type (`web` or `rag`), and source order. Raw unbounded search responses are not persisted or returned by default.

## API Contract

Existing `/api/research/execute/` remains compatible. The workspace uses a versioned logical flow under the existing API namespace:

- `POST /api/research/jobs/`: validate a bounded topic, create a session, execute through the service, and return a job representation. In the initial synchronous deployment, the request may finish before returning, but the object is created before work begins and has durable lifecycle state on every outcome.
- `GET /api/research/jobs/<id>/`: owner-only job detail including status, progress events, report metadata, evidence, and terminal error details.
- `GET /api/research/jobs/`: authenticated user’s paginated job/report library.
- `DELETE /api/research/jobs/<id>/`: owner-only deletion.

Responses use a consistent envelope where useful and stable machine-readable error codes. Topic input is trimmed, required, and length-limited. Unexpected exceptions are logged server-side and returned as a generic safe error.

## Workspace Experience

The Streamlit UI has four focused modes:

1. **Start research**: topic input, optional concise research-depth control, examples, API reachability feedback, and submit action.
2. **Run progress**: visible agent timeline, current stage, elapsed time, revision count, recoverable refresh, and clear terminal state.
3. **Report**: rendered Markdown, report metadata, verification verdict, evidence/source cards, and Markdown/text downloads.
4. **Library**: authenticated saved reports with status badges, pagination, detail navigation, and deletion confirmation.

The frontend retains a configurable `BACKEND_API_URL`, uses a small API client module with timeouts and friendly errors, and never exposes API keys. It presents empty, loading, unavailable, and failed states explicitly.

## Error Handling and Security

- All list/detail/delete endpoints require authenticated ownership, except explicitly public health/auth routes.
- The API never returns tracebacks, credentials, raw environment values, or unbounded provider payloads.
- Session creation happens before graph invocation. Failures transition the same record to `failed` and record a safe message, so users can see the job did not vanish.
- The existing direct graph endpoint remains supported, but shares validation and safe error behavior with the new service where possible.
- Development defaults are tightened: environment-controlled debug/hosts/CORS with local-safe defaults and documented production settings.

## Testing and Verification

Tests will stub graph execution and cover:

- Job creation, lifecycle states, events, sources, and terminal failures.
- Topic validation and safe error response shape.
- Authentication and ownership isolation for list/detail/delete endpoints.
- Existing auth, sessions, execute, and benchmark behavior to prevent regressions.
- Django system checks, migrations, and the full pytest suite.

Manual verification will run the Django service and Streamlit app locally, submit a topic through the workspace, observe progress, open the saved report, download it, and confirm it is only visible to its owner.

## Future Extension Points

The job model and progress contract permit future background workers, WebSockets, provider retry policies, richer citation extraction, and a standalone frontend without changing the core graph or user data model.

## Self-Review

- No placeholders or open TODOs remain.
- The data model, API contract, and UI all use Django as source of truth.
- The scope deliberately excludes queue/WebSocket infrastructure to keep the milestone deliverable.
- The initial synchronous execution behavior is explicit, avoiding a misleading claim of background processing.
