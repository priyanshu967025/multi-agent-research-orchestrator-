from state.schema import ResearchState
from config.setting import MODEL_NAME, get_groq_api_key
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """You are an expert analyst. From the data:
1. Identify 3-5 KEY THEMES
2. Note CONTRADICTIONS (conflicts between sources)
3. Highlight CONSENSUS points (where multiple sources agree)
4. Flag GAPS (what is missing)
Provide a structured output in Markdown."""

def get_llm():
    groq_key = get_groq_api_key()
    from langchain_groq import ChatGroq
    return ChatGroq(model=MODEL_NAME, temperature=0.2, groq_api_key=groq_key)

def analyst_node(state: ResearchState) -> dict:
    topic = state["topic"]
    research_data = state.get("research_data", [])
    rag_context = state.get("rag_context", [])

    compiled_data = "\n---\n".join(research_data[:10])

    rag_section = ""
    if rag_context:
        rag_section = f"\n\nDOCUMENT CONTEXT:\n" + "\n".join(rag_context[:5])

    groq_key = get_groq_api_key()
    analysis = ""
    try:
        if groq_key:
            llm = get_llm()
            response = llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"Topic: {topic}\nDATA:\n{compiled_data}{rag_section}"),
            ])
            analysis = response.content
        else:
            analysis = f"## Analysis for: {topic}\n\nData collected from {len(research_data)} sources.\n\n*(LLM analysis unavailable — GROQ_API_KEY is not configured in Streamlit Secrets or .env file)*"
    except Exception as e:
        analysis = f"## Analysis for: {topic}\n\nAnalysis generated with available data.\n\n*(Error: {e})*"

    return {
        "analysis": analysis,
        "messages": [f"📊 Analyst processed {len(research_data)} results."],
        "current_agent": "analyst",
    }
