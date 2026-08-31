from state.schema import ResearchState
from config.setting import get_tavily_api_key, MAX_SEARCH_RESULTS
from config.providers import get_llm_with_fallback
from langchain_core.messages import SystemMessage, HumanMessage

QUERY_GEN_PROMPT = """You are a research query strategist.
Given a research topic, generate exactly 3 diverse, specific search queries that will cover different angles of the topic.
Return ONLY the 3 queries, one per line. No numbering, no extra text."""

REVISION_PROMPT = """You are a research query strategist.
The fact-checker flagged issues with previous research. Based on the feedback below, generate 3 NEW, improved search queries that address the gaps and inaccuracies.
Return ONLY the 3 queries, one per line. No numbering, no extra text.

FACT-CHECKER FEEDBACK:
{feedback}"""

def get_llm():
    return get_llm_with_fallback(model=None, temperature=0.3)

def researcher_node(state: ResearchState) -> dict:
    topic = state["topic"]
    revision_count = state.get("revision_count", 0)

    sub_queries = [topic]

    try:
        llm = get_llm()
        if revision_count > 0 and state.get("fact_check_result"):
            prompt = REVISION_PROMPT.format(feedback=state["fact_check_result"])
        else:
            prompt = QUERY_GEN_PROMPT

        query_response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=f"Topic: {topic}"),
        ])
        lines = [l.strip() for l in query_response.content.strip().split("\n") if l.strip()]
        if lines:
            sub_queries = lines[:3]
    except Exception as e:
        sub_queries = [topic, f"{topic} latest research", f"{topic} analysis"]

    all_results = []
    tavily_key = get_tavily_api_key()

    try:
        if tavily_key:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_key)
            for query in sub_queries:
                try:
                    response = client.search(query=query, max_results=MAX_SEARCH_RESULTS)
                    for r in response.get("results", []):
                        all_results.append(f"[Source: {r.get('url', 'N/A')}]\n{r.get('content', '')}")
                except Exception as ex:
                    print(f"Tavily search error for query '{query}': {ex}")
                    continue

        # If Tavily was not used or yielded no results, fallback to DuckDuckGo search
        if not all_results:
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    for query in sub_queries:
                        results = list(ddgs.text(query, max_results=MAX_SEARCH_RESULTS))
                        for r in results:
                            all_results.append(f"[Source: {r.get('href', 'N/A')}]\nTitle: {r.get('title', '')}\n{r.get('body', '')}")
            except Exception as ddg_err:
                if not tavily_key:
                    all_results.append("[Notice] Tavily API Key not found. Please set TAVILY_API_KEY in .env file or Streamlit secrets.")
    except Exception as e:
        all_results.append(f"[Search Error] {str(e)}")

    rag_results = []
    try:
        from rag.vector_store import retrieve_context
        doc_context = retrieve_context(topic, collection_name="research_docs", k=5)
        past_context = retrieve_context(topic, collection_name="past_research", k=3)
        rag_results.extend(doc_context + past_context)
    except Exception:
        pass

    return {
        "research_data": all_results,
        "rag_context": rag_results,
        "messages": [f"🔍 Researcher found {len(all_results)} web results and {len(rag_results)} document chunks."],
        "current_agent": "researcher",
    }
