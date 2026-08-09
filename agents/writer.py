"""
✍️ Writer Agent
────────────────
Synthesizes the verified analysis and research data into a polished,
well-structured markdown report with inline citations, executive summary,
key findings, detailed sections, and a sources bibliography.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import MODEL_NAME
from state.schema import ResearchState

llm = ChatGroq(model=MODEL_NAME, temperature=0.3)

WRITER_SYSTEM_PROMPT = """You are an expert research report writer. You produce polished,
professional research reports in markdown format.

Your report MUST include these sections:
1. **Executive Summary** — 2-3 paragraph overview of the key findings
2. **Key Findings** — Bulleted list of the most important discoveries (with inline source citations)
3. **Detailed Analysis** — Deep dive into each major theme/finding with subsections
4. **Contradictions & Debates** — Any conflicting information found across sources
5. **Conclusion** — Synthesis of what the research tells us, and remaining open questions
6. **Sources** — Numbered list of all URLs referenced in the report

GUIDELINES:
- Use inline citations like [1], [2] that reference your Sources section
- Write in a clear, professional tone suitable for a business audience
- Use markdown formatting: headers, bullets, bold, blockquotes
- Include specific data points, statistics, and quotes where available
- The report should be comprehensive yet concise (800-1500 words)
- Do NOT fabricate information — only use what's in the provided data"""


def writer_node(state: ResearchState) -> dict:
    """
    Writer agent node for the LangGraph pipeline.

    Takes the verified analysis, fact-check results, raw research data,
    AND RAG context, then produces a polished markdown report with citations.
    Also stores the completed session in ChromaDB for future memory.
    """
    topic = state["topic"]
    analysis = state.get("analysis", "")
    fact_check_result = state.get("fact_check_result", "")
    research_data = state.get("research_data", [])
    rag_context = state.get("rag_context", [])

    # Extract source URLs for the bibliography
    sources = []
    for item in research_data:
        if "[Source:" in item:
            try:
                url = item.split("[Source: ")[1].split("]")[0]
                if url not in sources and url != "Unknown source":
                    sources.append(url)
            except (IndexError, ValueError):
                pass

    # Extract RAG document sources
    doc_sources = []
    for item in rag_context:
        if "[RAG Source:" in item:
            try:
                src = item.split("[RAG Source: ")[1].split("]")[0]
                if src not in doc_sources:
                    doc_sources.append(src)
            except (IndexError, ValueError):
                pass

    # Build combined sources list
    all_sources = []
    for url in sources:
        all_sources.append(url)
    for src in doc_sources:
        all_sources.append(f"📄 {src}")

    sources_text = "\n".join(f"[{i+1}] {src}" for i, src in enumerate(all_sources))
    compiled_data = "\n\n".join(research_data[:10])  # Cap to avoid token limits

    # Add RAG context section
    rag_section = ""
    if rag_context:
        compiled_rag = "\n\n".join(rag_context[:5])  # Cap RAG chunks too
        rag_section = f"""

DOCUMENT CONTEXT (from uploaded files & past research):
{compiled_rag}"""

    prompt = f"""Write a comprehensive research report on: "{topic}"

STRUCTURED ANALYSIS:
{analysis}

FACT-CHECK NOTES:
{fact_check_result}

RAW RESEARCH DATA (for additional detail and citations):
{compiled_data}
{rag_section}

AVAILABLE SOURCES FOR CITATION:
{sources_text}

Write the full report following your guidelines. Use the source numbers [1], [2], etc. 
for inline citations matching the AVAILABLE SOURCES list above.
Include both web and document sources in your citations where relevant."""

    response = llm.invoke([
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    report = response.content

    # ── Store session in ChromaDB for future memory ───────────────────
    try:
        from rag.vector_store import store_research_session
        chunks_stored = store_research_session(topic, research_data, report)
        memory_msg = f"💾 Stored {chunks_stored} chunks to research memory"
    except Exception:
        memory_msg = "💾 Memory storage skipped"

    return {
        "final_report": report,
        "messages": [
            "✍️ Writer: Final research report completed",
            memory_msg,
        ],
        "current_agent": "writer",
    }

