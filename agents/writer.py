from state.schema import ResearchState
from config.setting import MODEL_NAME, get_groq_api_key
from langchain_core.messages import SystemMessage, HumanMessage

WRITER_PROMPT = """You are a senior technical writer.
Synthesize the analysis and research data into a comprehensive, highly detailed, beautifully formatted Markdown research report.
Include an Executive Summary, Key Findings, In-depth Technical Breakdown, Consensus & Contradictions, and References/Citations."""

def get_llm():
    groq_key = get_groq_api_key()
    from langchain_groq import ChatGroq
    return ChatGroq(model=MODEL_NAME, temperature=0.4, groq_api_key=groq_key)

def writer_node(state: ResearchState) -> dict:
    topic = state["topic"]
    analysis = state.get("analysis", "")
    research_data = state.get("research_data", [])

    report = ""
    groq_key = get_groq_api_key()

    try:
        if groq_key:
            llm = get_llm()
            response = llm.invoke([
                SystemMessage(content=WRITER_PROMPT),
                HumanMessage(content=f"Topic: {topic}\nANALYSIS:\n{analysis}\nSOURCES:\n" + "\n".join(research_data[:8])),
            ])
            report = response.content
        else:
            report = f"# Research Report: {topic}\n\n## Executive Summary\n{analysis}\n\n## Sources\n" + "\n".join(research_data[:3])
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
