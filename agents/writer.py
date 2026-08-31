from state.schema import ResearchState
from config.providers import get_llm_with_fallback
from langchain_core.messages import SystemMessage, HumanMessage

WRITER_PROMPT = """You are a senior technical writer specializing in research communication.

Synthesize the analysis and research data into a comprehensive, publication-ready Markdown research report.

## Report Structure

Your report MUST include ALL of these sections:

### Executive Summary
- 3-5 sentence overview of the research
- Key finding in one sentence
- Overall assessment

### Table of Contents
- List all major sections with links

### Key Findings
- 3-7 major findings, each with:
  - Bold heading
  - 2-3 paragraph explanation
  - Supporting evidence from sources
  - Confidence level

### In-Depth Analysis
- Detailed technical breakdown of each theme
- Subsections for each major topic area
- Data points and specific examples

### Consensus & Contradictions
- Areas of agreement across sources
- Conflicting viewpoints and their implications
- How contradictions affect the overall picture

### Knowledge Gaps & Future Research
- What remains unknown
- Recommended areas for further investigation
- Methodology improvements for future research

### References
- Numbered list of all sources cited
- Full URLs where available
- Source type (web, academic, etc.)

## Writing Guidelines
- Use clear, professional language
- Define technical terms on first use
- Use specific data and examples
- Cite sources inline using [1], [2], etc.
- Write in third person
- Target length: 1500-3000 words"""

def get_llm():
    return get_llm_with_fallback(model=None, temperature=0.4)

def writer_node(state: ResearchState) -> dict:
    topic = state["topic"]
    analysis = state.get("analysis", "")
    research_data = state.get("research_data", [])

    trimmed_sources = [
        f"[{i+1}] {src[:350]}..." if len(src) > 350 else f"[{i+1}] {src}"
        for i, src in enumerate(research_data[:6])
    ]

    report = ""

    try:
        llm = get_llm()
        response = llm.invoke([
            SystemMessage(content=WRITER_PROMPT),
            HumanMessage(content=f"Topic: {topic}\nANALYSIS:\n{analysis[:3500]}\nSOURCES:\n" + "\n".join(trimmed_sources)),
        ])
        report = response.content
    except Exception as e:
        report = f"# Research Report: {topic}\n\n## Executive Summary\n{analysis}\n\n*(Report compiled with available data due to: {e})*"

    chunks_stored = 0
    try:
        from rag.vector_store import store_research_session
        chunks_stored = store_research_session(topic, research_data, report)
    except Exception as e:
        print(f"Memory store warning: {e}")

    return {
        "final_report": report,
        "messages": ["✍️ Report complete", f"💾 Saved {chunks_stored} chunks to vector memory."],
        "current_agent": "writer",
    }
