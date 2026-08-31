"""
MCP Server for the Multi-Agent Research Orchestrator.

Provides tools to run research pipelines, manage the RAG knowledge base,
query research sessions, and configure LLM providers.
"""

import sys
import os
from pydantic import BaseModel, Field, ConfigDict, field_validator
from fastmcp import FastMCP, Context
import httpx

# Ensure project root is importable.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Server ────────────────────────────────────────────────────────────

mcp = FastMCP(
    "research_orchestrator_mcp",
    instructions=(
        "Multi-Agent Research Orchestrator — 4 AI agents collaborate "
        "to research, analyze, fact-check, and write reports on any topic. "
        "Supports multiple LLM providers: Groq, OpenAI, Anthropic, and Ollama. "
        "Use these tools to run research, manage the knowledge base, and "
        "query research history."
    ),
)

# ── Input Models ──────────────────────────────────────────────────────

class ResearchTopicInput(BaseModel):
    """Input for running the full research pipeline."""
    model_config = ConfigDict(str_strip_whitespace=True)

    topic: str = Field(
        ...,
        description="The research topic or question to investigate (e.g., 'quantum computing advances 2025')",
        min_length=3,
        max_length=500,
    )


class SearchKnowledgeInput(BaseModel):
    """Input for searching the RAG knowledge base."""
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(
        ...,
        description="The search query (e.g., 'machine learning applications')",
        min_length=2,
        max_length=300,
    )
    num_results: int = Field(
        default=5,
        description="Number of results to return (1-20)",
        ge=1,
        le=20,
    )


class IngestDocumentInput(BaseModel):
    """Input for ingesting a PDF into the RAG knowledge base."""
    model_config = ConfigDict(str_strip_whitespace=True)

    file_path: str = Field(
        ...,
        description="Absolute path to the PDF file (e.g., 'C:/docs/paper.pdf')",
        min_length=1,
    )


class ListSessionsInput(BaseModel):
    """Input for listing research sessions."""
    page: int = Field(default=1, description="Page number (1-indexed)", ge=1)
    page_size: int = Field(default=20, description="Results per page (1-50)", ge=1, le=50)


class GetSessionInput(BaseModel):
    """Input for getting a specific research session."""
    session_id: int = Field(..., description="The research session ID", ge=1)


class AddTagInput(BaseModel):
    """Input for adding a tag to a research session."""
    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: int = Field(..., description="The research session ID", ge=1)
    tag_name: str = Field(
        ...,
        description="Tag name (e.g., 'machine-learning', 'quantum')",
        min_length=1,
        max_length=64,
    )

    @field_validator("tag_name")
    @classmethod
    def validate_tag(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("Tag name cannot be empty")
        return v


class RunBenchmarkInput(BaseModel):
    """Input for running a single vs multi-agent benchmark."""
    model_config = ConfigDict(str_strip_whitespace=True)

    topic: str = Field(
        ...,
        description="The benchmark topic (e.g., 'renewable energy policy')",
        min_length=3,
        max_length=500,
    )


# ── Helpers ───────────────────────────────────────────────────────────

def _get_api_base_url() -> str:
    """Return the Django API base URL from environment."""
    return os.environ.get("BACKEND_API_URL", "http://127.0.0.1:8000/api")


def _format_error(e: Exception) -> str:
    """Produce an actionable error message from an exception."""
    if isinstance(e, FileNotFoundError):
        return f"Error: File not found — {e}. Check the path is absolute and the file exists."
    name = type(e).__name__
    if "ConnectionRefused" in name or "ConnectionError" in name:
        return (
            "Error: Django backend is not running. "
            "Start it with: cd backend && python manage.py runserver 0.0.0.0:8000"
        )
    if "Timeout" in name:
        return "Error: Request timed out. The research pipeline may be processing a large topic — try again."
    return f"Error: {name}: {e}"


# ── Research Tools ────────────────────────────────────────────────────

@mcp.tool(
    name="research_orchestrator_research_topic",
    annotations={
        "title": "Run Multi-Agent Research",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def research_topic(params: ResearchTopicInput, ctx: Context) -> str:
    """Run the full 4-agent research pipeline (researcher → analyst → fact-checker → writer) on a topic.

    Produces a polished markdown report with citations, fact-check results, and
    revision history. Each agent stage is logged via the context for progress tracking.

    Args:
        params (ResearchTopicInput): Validated input containing:
            - topic (str): Research topic, 3-500 chars (e.g., "impact of CRISPR on agriculture")

    Returns:
        str: Markdown-formatted research report, or an error message.

    Examples:
        - "What are the latest advances in solid-state batteries?"
        - "Compare mRNA vaccine approaches for tropical diseases"
        - "Analyze the economic impact of remote work policies"
    """
    await ctx.report_progress(0.0, f"Starting research on: {params.topic}")
    await ctx.info(f"Research pipeline invoked for topic: {params.topic}")

    from graph.workflow import research_graph

    initial_state = {
        "topic": params.topic,
        "research_data": [],
        "analysis": "",
        "fact_check_result": "",
        "fact_check_passed": False,
        "revision_count": 0,
        "final_report": "",
        "rag_context": [],
        "messages": [],
        "current_agent": "",
        "error": "",
    }

    try:
        result = research_graph.invoke(initial_state, {"recursion_limit": 25})
        report = result.get("final_report", "No report generated.")
        revisions = result.get("revision_count", 0)
        sources = len(result.get("research_data", []))

        await ctx.report_progress(1.0, "Research complete")
        await ctx.info(f"Report generated: {sources} sources, {revisions} revisions")

        return (
            f"# Research Report: {params.topic}\n\n"
            f"**Sources:** {sources} | **Revisions:** {revisions}\n\n"
            f"---\n\n{report}"
        )
    except Exception as e:
        await ctx.log_error(f"Research failed: {e}")
        return _format_error(e)


@mcp.tool(
    name="research_orchestrator_get_provider_info",
    annotations={
        "title": "Get LLM Provider Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_provider_info() -> str:
    """Get information about available LLM providers and which one is currently active.

    Returns a summary showing the active provider, model, and availability status
    of all configured providers (Groq, OpenAI, Anthropic, Ollama).

    Returns:
        str: Markdown-formatted provider status table.

    Examples:
        - "Which LLM provider is configured?"
        - "Is Ollama available locally?"
    """
    from config.providers import provider_info

    info = provider_info()
    lines = [
        "## LLM Provider Status",
        "",
        f"- **Active Provider:** {info['active_provider']}",
        f"- **Model:** {info['model']}",
        "",
        "### Availability",
        "",
    ]
    for name, available in info["available"].items():
        status = "✅ Available" if available else "❌ Not configured"
        lines.append(f"- **{name.title()}:** {status}")

    return "\n".join(lines)


# ── Knowledge Base Tools ──────────────────────────────────────────────

@mcp.tool(
    name="research_orchestrator_ingest_document",
    annotations={
        "title": "Ingest PDF into Knowledge Base",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def ingest_document(params: IngestDocumentInput, ctx: Context) -> str:
    """Ingest a PDF document into the RAG knowledge base for future research context.

    Chunks the PDF and stores embeddings in ChromaDB. Ingested documents become
    searchable and are automatically included in research pipeline context.

    Args:
        params (IngestDocumentInput): Validated input containing:
            - file_path (str): Absolute path to the PDF file

    Returns:
        str: Status message with chunk count and file details.

    Examples:
        - Ingest a paper: file_path="/home/user/papers/transformer.pdf"
        - Ingest a report: file_path="C:/Documents/annual_report.pdf"
    """
    from rag.vector_store import ingest_documents

    if not os.path.exists(params.file_path):
        return f"Error: File not found: {params.file_path}. Verify the path is absolute and the file exists."

    await ctx.report_progress(0.5, f"Ingesting {params.file_path}...")

    try:
        result = ingest_documents([params.file_path])
        await ctx.report_progress(1.0, "Ingestion complete")
        return (
            f"✅ Ingested **{result['chunks_added']} chunks** from "
            f"`{', '.join(result['files_processed'])}`"
        )
    except Exception as e:
        await ctx.log_error(f"Ingestion failed: {e}")
        return _format_error(e)


@mcp.tool(
    name="research_orchestrator_search_knowledge_base",
    annotations={
        "title": "Search Knowledge Base",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def search_knowledge_base(params: SearchKnowledgeInput) -> str:
    """Search the RAG knowledge base for relevant document chunks.

    Searches both uploaded documents and past research memory. Returns the most
    relevant chunks ranked by semantic similarity.

    Args:
        params (SearchKnowledgeInput): Validated input containing:
            - query (str): Search query, min 2 chars
            - num_results (int): Number of results (1-20, default 5)

    Returns:
        str: Matching document chunks separated by dividers, or a "not found" message.

    Examples:
        - Search for "neural network architectures"
        - Search for "COVID vaccine efficacy data"
    """
    from rag.vector_store import retrieve_context

    results = retrieve_context(params.query, collection_name="research_docs", k=params.num_results)
    past = retrieve_context(params.query, collection_name="past_research", k=3)

    all_results = results + past
    if not all_results:
        return f"No relevant documents found for '{params.query}'. Try ingesting PDFs first with `research_orchestrator_ingest_document`."

    header = f"## Knowledge Base Results: \"{params.query}\"\n\n**{len(all_results)} chunks found**\n\n"
    chunks = "\n\n---\n\n".join(all_results)
    return header + chunks


@mcp.tool(
    name="research_orchestrator_get_kb_stats",
    annotations={
        "title": "Get Knowledge Base Statistics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_kb_stats() -> str:
    """Get statistics about the RAG knowledge base — chunk counts per collection.

    Returns:
        str: Markdown table showing document and research memory chunk counts.

    Examples:
        - "How many documents are in the knowledge base?"
        - "What's the RAG storage status?"
    """
    from rag.vector_store import get_collection_stats

    stats = get_collection_stats()
    docs = stats.get("research_docs", 0)
    memory = stats.get("past_research", 0)

    return (
        "## Knowledge Base Statistics\n\n"
        "| Collection | Chunks |\n"
        "|---|---|\n"
        f"| Uploaded Documents | {docs} |\n"
        f"| Research Memory | {memory} |\n"
        f"| **Total** | **{docs + memory}** |"
    )


@mcp.tool(
    name="research_orchestrator_clear_knowledge_base",
    annotations={
        "title": "Clear Knowledge Base",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def clear_knowledge_base() -> str:
    """Clear all documents from the RAG knowledge base (both uploads and research memory).

    This is destructive — ingested PDFs and past research context will be lost.
    You will need to re-ingest documents after clearing.

    Returns:
        str: Confirmation message.

    Examples:
        - "Clear the knowledge base to start fresh"
    """
    from rag.vector_store import clear_collection

    clear_collection("research_docs")
    clear_collection("past_research")
    return "✅ Knowledge base cleared. Re-ingest documents as needed."


# ── Session Management Tools ──────────────────────────────────────────

@mcp.tool(
    name="research_orchestrator_list_sessions",
    annotations={
        "title": "List Research Sessions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def list_sessions(params: ListSessionsInput, ctx: Context) -> str:
    """List research sessions for the authenticated user with pagination.

    Requires a valid auth token set as BACKEND_AUTH_TOKEN in the environment.

    Args:
        params (ListSessionsInput): Validated input containing:
            - page (int): Page number, 1-indexed (default 1)
            - page_size (int): Results per page, 1-50 (default 20)

    Returns:
        str: Paginated list of sessions with IDs, topics, statuses, and dates.

    Examples:
        - "Show my recent research sessions"
        - "List the next page of my research"
    """
    token = os.environ.get("BACKEND_AUTH_TOKEN", "")
    if not token:
        return "Error: No auth token. Set BACKEND_AUTH_TOKEN in the environment. Log in via the Streamlit UI first."

    await ctx.report_progress(0.3, "Fetching sessions...")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_get_api_base_url()}/research/sessions/",
                params={"page": params.page, "page_size": params.page_size},
                headers={"Authorization": f"Token {token}"},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()

        sessions = data.get("sessions", [])
        total = data.get("total", 0)

        if not sessions:
            return "No research sessions found. Run `research_orchestrator_research_topic` to create one."

        lines = [
            f"## Research Sessions (page {data['page']}/{(total + params.page_size - 1) // params.page_size})",
            "",
            f"**{total} total sessions**\n",
            "| ID | Topic | Status | Sources | Created |",
            "|---|---|---|---|---|",
        ]
        for s in sessions:
            created = s.get("created_at", "")[:10]
            lines.append(
                f"| {s['id']} | {s['topic'][:40]} | {s['status']} | {s.get('web_sources_count', 0)} | {created} |"
            )

        await ctx.report_progress(1.0, f"Found {total} sessions")
        return "\n".join(lines)

    except Exception as e:
        return _format_error(e)


@mcp.tool(
    name="research_orchestrator_get_session",
    annotations={
        "title": "Get Research Session Detail",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_session(params: GetSessionInput, ctx: Context) -> str:
    """Retrieve full details of a specific research session including the report.

    Args:
        params (GetSessionInput): Validated input containing:
            - session_id (int): The session ID to retrieve

    Returns:
        str: Full session details including topic, status, report, sources, tags, and timeline.

    Examples:
        - "Show me the full details of session 42"
        - "Get the report from research session 7"
    """
    token = os.environ.get("BACKEND_AUTH_TOKEN", "")
    if not token:
        return "Error: No auth token. Set BACKEND_AUTH_TOKEN in the environment."

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_get_api_base_url()}/research/sessions/{params.session_id}/",
                headers={"Authorization": f"Token {token}"},
                timeout=10.0,
            )
            if resp.status_code == 404:
                return f"Error: Session {params.session_id} not found. Check the session ID."
            resp.raise_for_status()
            s = resp.json()

        tags = s.get("tags", [])
        tag_str = ", ".join(t["name"] for t in tags) if tags else "none"
        events = s.get("timeline_events", [])

        lines = [
            f"## Session {s['id']}: {s['topic']}",
            "",
            f"- **Status:** {s['status']}",
            f"- **Created:** {s.get('created_at', 'N/A')}",
            f"- **Duration:** {s.get('duration_seconds', 'N/A')}s",
            f"- **Sources:** {s.get('web_sources_count', 0)} web, {s.get('rag_chunks_count', 0)} RAG",
            f"- **Revisions:** {s.get('revision_count', 0)}",
            f"- **Tags:** {tag_str}",
            "",
        ]

        if s.get("final_report"):
            lines.extend(["### Report", "", s["final_report"]])

        if events:
            lines.extend(["", "### Timeline", ""])
            for ev in events:
                lines.append(f"- **{ev.get('stage', '?')}:** {ev.get('message', '')[:120]}")

        return "\n".join(lines)

    except Exception as e:
        return _format_error(e)


@mcp.tool(
    name="research_orchestrator_add_tag",
    annotations={
        "title": "Add Tag to Research Session",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def add_tag(params: AddTagInput, ctx: Context) -> str:
    """Add a tag to a research session for organization and filtering.

    Tags are lowercased and deduplicated per session. If the tag already exists,
    it returns the existing tag without duplication.

    Args:
        params (AddTagInput): Validated input containing:
            - session_id (int): The session to tag
            - tag_name (str): Tag name, 1-64 chars, lowercased automatically

    Returns:
        str: Confirmation with the tag name and session ID.

    Examples:
        - Tag session 5 with "quantum-computing"
        - Add "urgent" tag to session 12
    """
    token = os.environ.get("BACKEND_AUTH_TOKEN", "")
    if not token:
        return "Error: No auth token. Set BACKEND_AUTH_TOKEN in the environment."

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_get_api_base_url()}/research/{params.session_id}/tags/",
                json={"name": params.tag_name},
                headers={"Authorization": f"Token {token}"},
                timeout=10.0,
            )
            if resp.status_code == 404:
                return f"Error: Session {params.session_id} not found."
            resp.raise_for_status()
            data = resp.json()

        created = resp.status_code == 201
        action = "Added" if created else "Already exists"
        return f"✅ {action} tag `{data['name']}` on session {params.session_id}"

    except Exception as e:
        return _format_error(e)


@mcp.tool(
    name="research_orchestrator_run_benchmark",
    annotations={
        "title": "Run Single vs Multi-Agent Benchmark",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def run_benchmark(params: RunBenchmarkInput, ctx: Context) -> str:
    """Run a benchmark comparing single-agent vs multi-agent research on a topic.

    Executes both a single-agent baseline and the full 4-agent pipeline, then
    evaluates depth and verifiability. Results are saved to benchmark history.

    Args:
        params (RunBenchmarkInput): Validated input containing:
            - topic (str): Benchmark topic, 3-500 chars

    Returns:
        str: Markdown comparison table with evaluation metrics.

    Examples:
        - "Benchmark: 'solar panel efficiency improvements'"
        - "Compare single vs multi-agent on 'AI regulation policies'"
    """
    await ctx.report_progress(0.0, f"Starting benchmark: {params.topic}")

    try:
        from benchmark.evaluator import run_single_agent_baseline, evaluate_outputs
        from graph.workflow import research_graph
        from config.providers import initial_research_state

        await ctx.report_progress(0.2, "Running single-agent baseline...")
        baseline = run_single_agent_baseline(params.topic)

        await ctx.report_progress(0.5, "Running multi-agent pipeline...")
        initial_state = initial_research_state(params.topic)
        pipeline_result = research_graph.invoke(initial_state, {"recursion_limit": 25})
        multi_report = pipeline_result.get("final_report", "")

        await ctx.report_progress(0.8, "Evaluating outputs...")
        metrics = evaluate_outputs(params.topic, baseline["text"], multi_report)

        await ctx.report_progress(1.0, "Benchmark complete")

        sa = metrics.get("single_agent", {})
        ma = metrics.get("multi_agent", {})

        return (
            f"## Benchmark: {params.topic}\n\n"
            "| Metric | Single Agent | Multi Agent |\n"
            "|---|---|---|\n"
            f"| Depth Score | {sa.get('depth_score', 0):.2f} | {ma.get('depth_score', 0):.2f} |\n"
            f"| Verifiability | {sa.get('verifiability_score', 0):.2f} | {ma.get('verifiability_score', 0):.2f} |\n\n"
            f"**Verdict:** {metrics.get('verdict', 'N/A')}"
        )

    except Exception as e:
        await ctx.log_error(f"Benchmark failed: {e}")
        return _format_error(e)


# ── Resources ─────────────────────────────────────────────────────────

@mcp.resource("info://orchestrator")
async def get_info() -> str:
    """Static information about the Research Orchestrator."""
    from config.providers import provider_info

    info = provider_info()
    return (
        "# Multi-Agent Research Orchestrator\n\n"
        "- **Version:** 2.0.0\n"
        "- **Agents:** Researcher, Analyst, Fact-Checker, Writer\n"
        f"- **Active LLM Provider:** {info['active_provider']}\n"
        f"- **Model:** {info['model']}\n"
        "- **Search:** Tavily (web) + ChromaDB (RAG)\n"
        "- **Features:** Feedback loop, PDF upload, research memory, multi-provider support"
    )


# ── Entry Point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
