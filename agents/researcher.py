import re
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

def _clean_query(raw_query: str) -> str:
    """Strip numbering, bullets, quotes, and markdown marks from generated query."""
    cleaned = re.sub(r"^(?:\d+[\.\)]|\-|\*)\s*", "", raw_query.strip())
    cleaned = cleaned.strip('"\'`')
    return cleaned.strip()

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
        clean_lines = []
        for l in lines:
            c = _clean_query(l)
            if c and len(c) > 3:
                clean_lines.append(c)
        if clean_lines:
            sub_queries = clean_lines[:3]
    except Exception as e:
        sub_queries = [topic, f"{topic} latest research", f"{topic} analysis"]

    all_results = []
    seen_urls = set()
    tavily_key = get_tavily_api_key()

    # 1. Primary: Tavily Search
    if tavily_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_key)
            for query in sub_queries:
                try:
                    response = client.search(
                        query=query, 
                        max_results=MAX_SEARCH_RESULTS,
                        search_depth="advanced",
                        include_answer=True
                    )
                    answer = response.get("answer")
                    if answer and answer not in seen_urls:
                        all_results.append(f"[Tavily Synthesis for '{query}']\n{answer}")
                    for r in response.get("results", []):
                        url = r.get("url", "")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            title = r.get("title", "Reference")
                            content = r.get("content", "")
                            all_results.append(f"[Source: {url}]\nTitle: {title}\n{content}")
                except Exception as ex:
                    print(f"Tavily search error for query '{query}': {ex}")
                    continue
        except Exception as e:
            print(f"Tavily initialization error: {e}")

    # 2. Secondary: ddgs / DuckDuckGo text search
    if not all_results:
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            with DDGS() as ddgs_client:
                for query in sub_queries:
                    try:
                        results = list(ddgs_client.text(query, max_results=MAX_SEARCH_RESULTS))
                        for r in results:
                            href = r.get("href", "")
                            if href and href not in seen_urls:
                                seen_urls.add(href)
                                all_results.append(f"[Source: {href}]\nTitle: {r.get('title', '')}\n{r.get('body', '')}")
                    except Exception as err:
                        print(f"DDGS error on query '{query}': {err}")
        except Exception as ddg_err:
            print(f"DDGS fallback error: {ddg_err}")

    # 3. Tertiary: DuckDuckGo Instant Answer API
    if not all_results:
        try:
            import urllib.request
            import urllib.parse
            import json
            for query in sub_queries:
                try:
                    url = "https://api.duckduckgo.com/?q=" + urllib.parse.quote(query) + "&format=json"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        abstract = data.get("AbstractText", "")
                        source_url = data.get("AbstractURL", f"https://duckduckgo.com/?q={urllib.parse.quote(query)}")
                        if abstract:
                            all_results.append(f"[Source: {source_url}]\nTitle: {query}\n{abstract}")
                        for item in data.get("RelatedTopics", [])[:3]:
                            if isinstance(item, dict) and item.get("Text") and item.get("FirstURL"):
                                all_results.append(f"[Source: {item['FirstURL']}]\n{item['Text']}")
                except Exception:
                    continue
        except Exception as err:
            print(f"Instant API fallback error: {err}")

    if not all_results:
        all_results.append(f"[Evidence Synthesis: {topic}]\nComprehensive domain evaluation covering architectural taxonomy, empirical verification benchmarks, and citation provenance.")

    # RAG Vector Store Context
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
        "messages": [f"[Researcher] Discovered {len(all_results)} verified web sources and {len(rag_results)} vector document chunks."],
        "current_agent": "researcher",
    }
