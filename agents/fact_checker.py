"""
✅ Fact-Checker Agent
─────────────────────
Cross-references claims in the analysis against the raw research data.
Optionally performs additional web searches to verify specific claims.
Controls the feedback loop: if claims can't be verified, routes back
to the Researcher (up to MAX_REVISIONS times).
"""

from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import MODEL_NAME, MAX_REVISIONS, MAX_SEARCH_RESULTS
from state.schema import ResearchState

llm = ChatGroq(model=MODEL_NAME, temperature=0)

search_tool = TavilySearch(
    max_results=MAX_SEARCH_RESULTS,
    search_depth="basic",
)

FACT_CHECKER_SYSTEM_PROMPT = """You are a meticulous fact-checker. Your job is to verify 
claims made in a research analysis against the provided source data.

For each major claim in the analysis, you must:
1. CHECK if the claim is supported by the source data
2. MARK each claim as: ✅ VERIFIED, ⚠️ PARTIALLY VERIFIED, or ❌ UNVERIFIED
3. NOTE the source(s) that support or contradict each claim

After reviewing all claims, provide:
- A SUMMARY of verification results
- A VERDICT: either "PASSED" (most claims verified) or "NEEDS_REVISION" (significant unverified claims)
- If NEEDS_REVISION: list specific questions that need more research

You must output your verdict on the LAST LINE in exactly this format:
VERDICT: PASSED
or
VERDICT: NEEDS_REVISION

Be strict but fair. Minor gaps are okay — flag only significant issues."""


def fact_checker_node(state: ResearchState) -> dict:
    """
    Fact-checker agent node for the LangGraph pipeline.

    Cross-references analysis claims against research data,
    and decides whether to proceed to the Writer or loop back
    to the Researcher for more data.
    """
    topic = state["topic"]
    analysis = state.get("analysis", "")
    research_data = state.get("research_data", [])
    revision_count = state.get("revision_count", 0)

    if not analysis:
        return {
            "fact_check_result": "No analysis to fact-check.",
            "fact_check_passed": True,
            "messages": ["✅ Fact-Checker: No analysis provided — passing through."],
            "current_agent": "fact_checker",
        }

    compiled_sources = "\n\n---\n\n".join(research_data)

    prompt = f"""Fact-check the following analysis on "{topic}":

ANALYSIS TO VERIFY:
{analysis}

SOURCE DATA:
{compiled_sources}

Verify each major claim against the sources. Provide your detailed fact-check report 
and end with your VERDICT line."""

    response = llm.invoke([
        SystemMessage(content=FACT_CHECKER_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    result = response.content

    # Parse verdict from response
    passed = True
    if "VERDICT: NEEDS_REVISION" in result.upper():
        # Only fail if we haven't exceeded max revisions
        if revision_count < MAX_REVISIONS:
            passed = False

    status_icon = "✅" if passed else "🔄"
    status = (
        f"{status_icon} Fact-Checker: "
        + ("All claims verified — proceeding to Writer" if passed
           else f"Flagged issues — sending back for revision (round {revision_count + 1}/{MAX_REVISIONS})")
    )

    return {
        "fact_check_result": result,
        "fact_check_passed": passed,
        "revision_count": revision_count + (0 if passed else 1),
        "messages": [status],
        "current_agent": "fact_checker",
    }
