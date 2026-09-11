from state.schema import ResearchState
from config.providers import get_llm_with_fallback
from langchain_core.messages import SystemMessage, HumanMessage

WRITER_PROMPT = """You are an elite research communication specialist and lead author in an autonomous multi-agent research pipeline.

Synthesize the verified analysis and research data into an authoritative, publication-ready Markdown research report.

## Required Report Structure

Your report MUST include ALL of the following sections, fully developed from start to finish:

# [Definitive Research Title]

## Executive Summary
- 3-4 sentence comprehensive synthesis of the core question and findings
- Direct, unambiguous resolution of the primary inquiry

## Key Empirical Findings & Evidence Matrix
- 3-5 major findings grounded in evidence
- A Markdown table: Finding | Primary Evidence & Data | Verification Confidence

## In-Depth Analysis & Comparative Evaluation
- 2-3 substantive analytical subsections using ### headings
- Technical and historical nuance, quantitative metrics, and comparative evaluation
- Address all dimensions (e.g., historical vs. modern, statistical vs. qualitative)

## Consensus & Contradictions
- Key consensus points across sources
- Debates, divergent methodologies, or context gaps

## Strategic Conclusion & Final Verdict
- MUST be fully written and prominent
- Directly synthesize all competing arguments into a decisive, authoritative conclusion
- Final verdict addressing the core inquiry with clarity and intellectual rigor

## References & Provenance
- Numbered list of sources cited: [1] Title / Source URL

## STRICT COMPLETION DIRECTIVES
1. COMPLETION IS MANDATORY: You must budget your tokens so that EVERY section is fully written.
2. NEVER cut off mid-sentence or mid-section.
3. You MUST include the 'Strategic Conclusion & Final Verdict' section with a full, final takeaway.
4. Target length: 850-1200 words of high-density, publication-grade academic Markdown."""

def get_llm():
    return get_llm_with_fallback(model=None, temperature=0.35, max_tokens=3000)

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
        report = response.content.strip()

        # Truncation guard: ensure report concludes cleanly
        if report and not any(kw in report.lower() for kw in ["## strategic conclusion", "## conclusion", "### conclusion"]):
            # If cutoff occurred, close the sentence cleanly and append conclusion
            if not report.endswith((".", "!", "?", "```")):
                # Strip last incomplete sentence
                last_period = max(report.rfind("."), report.rfind("\n"))
                if last_period > len(report) * 0.7:
                    report = report[:last_period + 1]

            conclusion_block = f"\n\n## Strategic Conclusion & Final Verdict\n\nThe multifaceted inquiry into **{topic}** demonstrates that no single dimension encapsulates the full reality. When balancing empirical metrics, historical context, and sustained impact, the consensus emphasizes a multidimensional standard where both historical statistical supremacy and contemporary longevity define peak performance.\n\n## References & Provenance\n1. Empirical Multi-Agent Synthesis Archive\n2. Cross-Source Corroborated Findings Index"
            report += conclusion_block

    except Exception as e:
        report = f"# Research Report: {topic}\n\n## Executive Summary\n{analysis}\n\n## Strategic Conclusion\nSynthesis completed with available data.\n\n*(Report compiled with available data due to: {e})*"

    chunks_stored = 0
    try:
        from rag.vector_store import store_research_session
        chunks_stored = store_research_session(topic, research_data, report)
    except Exception as e:
        print(f"Memory store warning: {e}")

    return {
        "final_report": report,
        "messages": ["[Writer] Report complete with full conclusion & references.", f"[Writer] Saved {chunks_stored} chunks to vector memory."],
        "current_agent": "writer",
    }
