import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP

mcp = FastMCP(
    "ResearchOrchestrator",
    description="Multi-Agent Research Orchestrator — 4 AI agents collaborate "
                "to research, analyze, fact-check, and write reports on any topic."
)


@mcp.tool()
def research_topic(topic: str) -> str:
    """
    Run the full multi-agent research pipeline on a topic.

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
        return result.get("final_report", "No report generated.")
    except Exception as e:
        return f"Error during research: {str(e)}"


@mcp.tool()
def ingest_document(file_path: str) -> str:
    """
    Ingest a PDF document into the RAG knowledge base.

    Args:
        file_path: Absolute path to the PDF file.

    Returns:
        Status message with number of chunks ingested.
    """
    from rag.vector_store import ingest_documents

    if not os.path.exists(file_path):
        return f"Error: File not found: {file_path}"

    result = ingest_documents([file_path])
    return (
        f"Ingested {result['chunks_added']} chunks from "
        f"{', '.join(result['files_processed'])}"
    )


@mcp.tool()
def search_knowledge_base(query: str, num_results: int = 5) -> str:
    """
    Search the RAG knowledge base for relevant information.

    Args:
        query: The search query.
        num_results: Number of results to return (default: 5).

    Returns:
        Relevant document chunks matching the query.
    """
    from rag.vector_store import retrieve_context

    results = retrieve_context(query, collection_name="research_docs", k=num_results)
    past = retrieve_context(query, collection_name="past_research", k=3)

    all_results = results + past

    if not all_results:
        return "No relevant documents found in the knowledge base."

    return "\n\n---\n\n".join(all_results)


@mcp.tool()
def get_kb_stats() -> str:
    """Get statistics about the RAG knowledge base."""
    from rag.vector_store import get_collection_stats

    stats = get_collection_stats()
    return (
        f"Knowledge Base Stats:\n"
        f"  Uploaded Documents: {stats.get('research_docs', 0)} chunks\n"
        f"  Research Memory: {stats.get('past_research', 0)} chunks"
    )


@mcp.tool()
def clear_knowledge_base() -> str:
    """Clear all documents from the RAG knowledge base."""
    from rag.vector_store import clear_collection

    clear_collection("research_docs")
    clear_collection("past_research")
    return "Knowledge base cleared successfully."


@mcp.resource("info://orchestrator")
def get_info() -> str:
    """Information about the Research Orchestrator."""
    return """
    Multi-Agent Research Orchestrator
    Version: 1.0.0
    Agents: Researcher, Analyst, Fact-Checker, Writer
    LLM: Groq (llama-3.3-70b-versatile)
    Search: Tavily (web) + ChromaDB (RAG)
    Features: Feedback loop, PDF upload, research memory
    """


if __name__ == "__main__":
    mcp.run(transport="stdio")
