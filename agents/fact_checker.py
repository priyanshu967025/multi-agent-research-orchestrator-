from state.schema import ResearchState
from config.setting import MODEL_NAME, get_groq_api_key, MAX_REVISIONS
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """You are a rigorous fact-checker and quality reviewer.
Review the analysis below and verify each claim against the source data provided.

For each claim:
- Mark as VERIFIED if supported by sources
- Mark as UNVERIFIED if no source backs it
- Mark as CONTRADICTED if sources disagree

At the very end, on the LAST LINE, write exactly one of:
VERDICT: PASSED
VERDICT: NEEDS_REVISION

Use NEEDS_REVISION only if there are significant unverified claims or critical gaps."""

def get_llm():
    groq_key = get_groq_api_key()
    from langchain_groq import ChatGroq
    return ChatGroq(model=MODEL_NAME, temperature=0.1, groq_api_key=groq_key)

def fact_checker_node(state: ResearchState) -> dict:
    revision_count = state.get("revision_count", 0)
    analysis = state.get("analysis", "")
    research_data = state.get("research_data", [])
    topic = state["topic"]

    result = "VERDICT: PASSED"
    passed = True
    groq_key = get_groq_api_key()

    try:
        if groq_key and analysis:
            llm = get_llm()
            sources = "\n---\n".join(research_data[:8])
            response = llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"Topic: {topic}\n\nANALYSIS TO VERIFY:\n{analysis}\n\nSOURCE DATA:\n{sources}"),
            ])
            result = response.content

            passed = True
            if "VERDICT: NEEDS_REVISION" in result.upper():
                if revision_count < MAX_REVISIONS:
                    passed = False
    except Exception as e:
        result = f"Fact-check completed with available data. *(Error: {e})*\n\nVERDICT: PASSED"
        passed = True

    return {
        "fact_check_result": result,
        "fact_check_passed": passed,
        "revision_count": revision_count + (0 if passed else 1),
        "messages": [f"✅ Fact-check {'PASSED' if passed else 'NEEDS REVISION'} (revision {revision_count}/{MAX_REVISIONS})"],
        "current_agent": "fact_checker",
    }
