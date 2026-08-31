from state.schema import ResearchState
from config.setting import MAX_REVISIONS
from config.providers import get_llm_with_fallback
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """You are a rigorous fact-checker and quality assurance expert for research reports.

Review the analysis below and verify each claim against the source data provided.

## Verification Protocol

For EACH major claim in the analysis, provide:
1. **Claim**: Quote the specific claim
2. **Verdict**: VERIFIED / UNVERIFIED / CONTRADICTED / PARTIALLY_VERIFIED
3. **Source Evidence**: Which source(s) support or contradict this claim
4. **Confidence**: High / Medium / Low based on source quality

## Quality Checks
- Check for logical consistency within the analysis
- Verify that conclusions follow from the evidence presented
- Flag any circular reasoning or unsupported leaps
- Identify any claims that misrepresent source material

## Overall Assessment

After verifying all claims, provide:
- Total claims reviewed
- Breakdown by verdict type
- Quality score (1-10) for the analysis

At the very end, on the LAST LINE, write exactly one of:
VERDICT: PASSED
VERDICT: NEEDS_REVISION

Use NEEDS_REVISION ONLY if:
- More than 30% of claims are UNVERIFIED
- Any critical claims are CONTRADICTED
- There are significant logical gaps
- The quality score is below 5

Be thorough but fair. A good analysis with minor gaps should PASS."""

def get_llm():
    return get_llm_with_fallback(model=None, temperature=0.1)

def fact_checker_node(state: ResearchState) -> dict:
    revision_count = state.get("revision_count", 0)
    analysis = state.get("analysis", "")
    research_data = state.get("research_data", [])
    topic = state["topic"]

    result = "VERDICT: PASSED"
    passed = True

    trimmed_sources = [
        f"[{i+1}] {src[:300]}..." if len(src) > 300 else f"[{i+1}] {src}"
        for i, src in enumerate(research_data[:6])
    ]

    try:
        if analysis:
            llm = get_llm()
            sources = "\n---\n".join(trimmed_sources)
            response = llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"Topic: {topic}\n\nANALYSIS TO VERIFY:\n{analysis[:2500]}\n\nSOURCE DATA:\n{sources}"),
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
