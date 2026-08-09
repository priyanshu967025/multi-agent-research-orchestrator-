"""
🔍 Researcher Agent
───────────────────
Uses Tavily web search AND ChromaDB RAG to gather comprehensive data.
Strategy: generates 3 strategic sub-queries from the main topic, then
searches BOTH the web (Tavily) and uploaded documents (ChromaDB),
aggregating all results with source URLs for downstream citation.
"""

import asyncio
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import MODEL_NAME, MAX_SEARCH_RESULTS
from state.schema import ResearchState


# ── Tool setup ────────────────────────────────────────────────────────
search_tool = TavilySearch(
    max_results=MAX_SEARCH_RESULTS,
    search_depth="advanced",
)

llm = ChatGroq(model=MODEL_NAME, temperature=0)


async def _async_search_single(query: str) -> list[str]:
    """Execute a single Tavily search asynchronously."""
    try:
        results = await search_tool.ainvoke({"query": query})
        output = []
        if isinstance(results, list):
            for r in results:
                if isinstance(r, dict):
                    source = r.get("url", "Unknown source")
                    content = r.get("content", "")
                    output.append(f"[Source: {source}]\n{content}")
                else:
                    output.append(str(r))
        elif isinstance(results, str):
            output.append(results)
        return output
    except Exception as e:
        # Fallback to sync invoke if ainvoke encounters an issue
        try:
            results = search_tool.invoke({"query": query})
            output = []
            if isinstance(results, list):
                for r in results:
                    if isinstance(r, dict):
                        source = r.get("url", "Unknown source")
                        content = r.get("content", "")
                        output.append(f"[Source: {source}]\n{content}")
                    else:
                        output.append(str(r))
            elif isinstance(results, str):
                output.append(results)
            return output
        except Exception as sync_e:
            return [f"[Search error for '{query}']: {str(sync_e)}"]


async def _run_concurrent_searches(sub_queries: list[str]) -> list[str]:
    """Run all sub-queries concurrently using asyncio.gather for maximum speed."""
    tasks = [_async_search_single(q) for q in sub_queries]
    results_nested = await asyncio.gather(*tasks, return_exceptions=True)
    
    flat_results = []
    for res in results_nested:
        if isinstance(res, Exception):
            flat_results.append(f"[Search execution error]: {str(res)}")
        elif isinstance(res, list):
            flat_results.extend(res)
    return flat_results


def researcher_node(state: ResearchState) -> dict:
    """
    Researcher agent node for the LangGraph pipeline.

    1. Uses the LLM to generate focused sub-queries from the topic.
    2. Runs sub-queries CONCURRENTLY using asyncio.gather for high speed.
    3. Queries ChromaDB for relevant uploaded document context (RAG).
    4. Aggregates all results with source attribution.
    """
    topic = state["topic"]
    revision_count = state.get("revision_count", 0)

    # If this is a revision loop, use fact-checker feedback to refine queries
    if revision_count > 0 and state.get("fact_check_result"):
        query_prompt = f"""You are a research strategist. A fact-checker has flagged issues 
with previous research on: "{topic}"

Fact-checker feedback:
{state['fact_check_result']}

Generate exactly 3 targeted search queries to fill the gaps and verify 
the flagged claims. Return ONLY the 3 queries, one per line, no numbering or bullets."""
    else:
        query_prompt = f"""You are a research strategist. Generate exactly 3 focused, 
diverse search queries to comprehensively research this topic: "{topic}"

Cover different angles: factual data, expert opinions, and recent developments.
Return ONLY the 3 queries, one per line, no numbering or bullets."""

    # Generate sub-queries
    query_response = llm.invoke([
        SystemMessage(content="You are a research query generator. Output only the queries, nothing else."),
        HumanMessage(content=query_prompt),
    ])

    sub_queries = [q.strip() for q in query_response.content.strip().split("\n") if q.strip()]
    sub_queries = sub_queries[:3]  # Safety cap

    # If LLM fails to generate queries, fall back to the topic itself
    if not sub_queries:
        sub_queries = [topic]

    # ── Concurrent Web Search (Tavily + asyncio.gather) ────────────────
    try:
        # Check if an event loop is already running (e.g. inside Streamlit or FastAPI/Django)
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                all_results = loop.run_until_complete(_run_concurrent_searches(sub_queries))
            else:
                all_results = loop.run_until_complete(_run_concurrent_searches(sub_queries))
        except RuntimeError:
            all_results = asyncio.run(_run_concurrent_searches(sub_queries))
    except Exception as e:
        # Fallback to sync sequential search if event loop management encounters edge cases
        all_results = []
        for q in sub_queries:
            try:
                res = search_tool.invoke({"query": q})
                if isinstance(res, list):
                    for r in res:
                        if isinstance(r, dict):
                            all_results.append(f"[Source: {r.get('url', 'Unknown')}]\n{r.get('content', '')}")
                        else:
                            all_results.append(str(r))
            except Exception as se:
                all_results.append(f"[Search error]: {str(se)}")

    # ── RAG Retrieval (ChromaDB) ──────────────────────────────────────
    rag_results = []
    try:
        from rag.vector_store import retrieve_context

        # Search uploaded documents
        doc_context = retrieve_context(topic, collection_name="research_docs", k=5)
        if doc_context:
            rag_results.extend(doc_context)

        # Search past research memory
        past_context = retrieve_context(topic, collection_name="past_research", k=3)
        if past_context:
            rag_results.extend(past_context)

    except Exception as e:
        rag_results.append(f"[RAG retrieval note]: {str(e)}")

    # ── Status Message ────────────────────────────────────────────────
    rag_count = len([r for r in rag_results if not r.startswith("[RAG retrieval note]")])
    status = (
        f"⚡ Researcher (Async): Searched {len(sub_queries)} queries concurrently, "
        f"retrieved {len(all_results)} web results"
        + (f" + {rag_count} RAG document chunks" if rag_count > 0 else "")
        + (" (revision round)" if revision_count > 0 else "")
    )

    return {
        "research_data": all_results,
        "rag_context": rag_results,
        "messages": [status],
        "current_agent": "researcher",
    }

