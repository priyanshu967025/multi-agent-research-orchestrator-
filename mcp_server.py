"""
🔌 MCP Server — Research Orchestrator as a Tool
────────────────────────────────────────────────
Exposes the multi-agent research pipeline as MCP tools.
Any MCP-compatible client (Claude Desktop, Cursor, etc.)
can call these tools directly.

Usage:
    # Test with MCP Inspector
    fastmcp dev mcp_server.py

    # Run as stdio server (for Claude Desktop / Cursor)
    python mcp_server.py
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP

# ── Initialize MCP Server ────────────────────────────────────────────
mcp = FastMCP(
    "ResearchOrchestrator",
    description=(
        "Multi-Agent Research Orchestrator — 4 AI agents collaborate "
        "to research, analyze, fact-check, and write reports on any topic. "
        "Features RAG with ChromaDB for PDF document search and research memory."
    ),
)


# ── Tool 1: Research a Topic ─────────────────────────────────────────
@mcp.tool()
def research_topic(topic: str) -> str:
    """
    Run the full multi-agent research pipeline on a topic.
    4 agents (Researcher, Analyst, Fact-Checker, Writer) collaborate
    to produce a comprehensive, fact-checked, cited research report.

    Args:
        topic: The research topic or question to investigate.

    Returns:
        A polished markdown research report with citations.
    """
    from graph.workflow import research_graph

    initial_state = {
        "topic": topic,
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
        report = result.get("final_report", "")
        if report:
            return report
        elif result.get("error"):
            return f"Pipeline error: {result['error']}"
        else:
            return "No report was generated. Please try a different topic."
    except Exception as e:
        return f"Error during research: {str(e)}"


# ── Tool 2: Upload Document to Knowledge Base ────────────────────────
@mcp.tool()
def ingest_document(file_path: str) -> str:
    """
    Ingest a PDF document into the RAG knowledge base.
    Once ingested, the document's contents will be automatically
    searched during research for richer, more contextual reports.

    Args:
        file_path: Absolute path to the PDF file to ingest.

    Returns:
        Status message with the number of chunks ingested.
    """
    from rag.vector_store import ingest_documents

    if not os.path.exists(file_path):
        return f"Error: File not found at '{file_path}'"

    if not file_path.lower().endswith(".pdf"):
        return "Error: Only PDF files are supported."

    try:
        result = ingest_documents([file_path])
        return (
            f"✅ Ingested {result['chunks_added']} chunks from "
            f"{', '.join(result['files_processed'])}"
        )
    except Exception as e:
        return f"Error during ingestion: {str(e)}"


# ── Tool 3: Search Knowledge Base ────────────────────────────────────
@mcp.tool()
def search_knowledge_base(query: str, num_results: int = 5) -> str:
    """
    Search the RAG knowledge base for relevant information from
    uploaded documents and past research sessions.

    Args:
        query: The search query.
        num_results: Number of results to return (default: 5).

    Returns:
        Relevant document chunks matching the query.
    """
    from rag.vector_store import retrieve_context

    try:
        doc_results = retrieve_context(
            query, collection_name="research_docs", k=num_results
        )
        past_results = retrieve_context(
            query, collection_name="past_research", k=3
        )

        all_results = doc_results + past_results

        if not all_results:
            return "No relevant documents found in the knowledge base."

        return "\n\n---\n\n".join(all_results)
    except Exception as e:
        return f"Error during search: {str(e)}"


# ── Tool 4: Knowledge Base Stats ─────────────────────────────────────
@mcp.tool()
def get_kb_stats() -> str:
    """Get statistics about the RAG knowledge base — number of stored chunks."""
    from rag.vector_store import get_collection_stats

    try:
        stats = get_collection_stats()
        return (
            f"📚 Knowledge Base Stats:\n"
            f"  📄 Uploaded Documents: {stats.get('research_docs', 0)} chunks\n"
            f"  🧠 Research Memory: {stats.get('past_research', 0)} chunks"
        )
    except Exception as e:
        return f"Error fetching stats: {str(e)}"


# ── Tool 5: Clear Knowledge Base ─────────────────────────────────────
@mcp.tool()
def clear_knowledge_base() -> str:
    """Clear all documents and research memory from the RAG knowledge base."""
    from rag.vector_store import clear_collection

    try:
        clear_collection("research_docs")
        clear_collection("past_research")
        return "✅ Knowledge base cleared successfully."
    except Exception as e:
        return f"Error clearing knowledge base: {str(e)}"


# ── Resource: Project Info ────────────────────────────────────────────
@mcp.resource("info://orchestrator")
def get_info() -> str:
    """Detailed information about the Research Orchestrator system."""
    return """
Multi-Agent Research Orchestrator v1.0
══════════════════════════════════════

Agents:
  🔍 Researcher  — Web search (Tavily) + RAG document retrieval (ChromaDB)
  📊 Analyst     — Pattern extraction, theme identification, gap analysis
  ✅ Fact Checker — Claim verification with feedback loop (max 2 revisions)
  ✍️ Writer      — Report synthesis with citations + session memory storage

Tech Stack:
  • LLM: Groq (llama-3.3-70b-versatile)
  • Search: Tavily (advanced depth)
  • Vector Store: ChromaDB (persistent)
  • Embeddings: HuggingFace all-MiniLM-L6-v2 (free, local)
  • Orchestration: LangGraph StateGraph
  • UI: Streamlit (glassmorphism dark theme)
  • Protocol: MCP (Model Context Protocol)

Pipeline:
  Researcher → Analyst → Fact-Checker → Writer
                           ↑     ↓
                           └─────┘ (revision loop)
"""


# ── Run Server ────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
