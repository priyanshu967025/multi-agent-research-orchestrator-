from state.schema import ResearchState
from config.providers import get_llm_with_fallback
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """You are an expert research analyst with deep expertise in synthesizing complex information.

Given the research data below, produce a structured analysis following this format:

## Key Themes
Identify 3-5 major themes from the data. For each theme, provide:
- A clear heading
- A 2-3 sentence explanation
- Supporting evidence from the sources

## Source Contradictions
Note any conflicts or contradictions between different sources. For each:
- State the contradictory claims
- Identify which sources disagree
- Assess which claim appears more credible and why

## Consensus Points
Highlight areas where multiple sources agree. Include:
- What the consensus is
- How many sources support it
- The strength of the agreement

## Knowledge Gaps
Flag what is missing from the research:
- Topics not covered by available sources
- Questions that remain unanswered
- Areas needing more investigation

## Confidence Assessment
Rate your overall confidence in the analysis (High/Medium/Low) and explain why.

Be precise, cite specific sources, and distinguish between facts and interpretations."""

def get_llm():
    return get_llm_with_fallback(model=None, temperature=0.2)

def analyst_node(state: ResearchState) -> dict:
    topic = state["topic"]
    research_data = state.get("research_data", [])
    rag_context = state.get("rag_context", [])

    trimmed_sources = [
        f"Source {i+1}: {src[:450]}..." if len(src) > 450 else f"Source {i+1}: {src}"
        for i, src in enumerate(research_data[:8])
    ]
    compiled_data = "\n---\n".join(trimmed_sources)

    rag_section = ""
    if rag_context:
        trimmed_rag = [
            f"Doc Chunk {i+1}: {chunk[:350]}..." if len(chunk) > 350 else f"Doc Chunk {i+1}: {chunk}"
            for i, chunk in enumerate(rag_context[:4])
        ]
        rag_section = f"\n\nDOCUMENT CONTEXT:\n" + "\n".join(trimmed_rag)

    analysis = ""
    try:
        llm = get_llm()
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Topic: {topic}\nDATA:\n{compiled_data}{rag_section}"),
        ])
        analysis = response.content
    except Exception as e:
        analysis = f"## Analysis for: {topic}\n\nAnalysis generated with available data.\n\n*(Error: {e})*"

    return {
        "analysis": analysis,
        "messages": [f"📊 Analyst processed {len(research_data)} results."],
        "current_agent": "analyst",
    }
