"""
📊 Analyst Agent
────────────────
Takes raw research data from the Researcher and extracts structured
insights: key themes, patterns, contradictions, and consensus points.
Produces a well-organized analysis for the Fact-Checker and Writer.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import MODEL_NAME
from state.schema import ResearchState

llm = ChatGroq(model=MODEL_NAME, temperature=0.1)

ANALYST_SYSTEM_PROMPT = """You are an expert research analyst. Your job is to synthesize 
raw research data into a clear, structured analysis.

You MUST:
1. Identify 3-5 KEY THEMES or findings from the data
2. Note any CONTRADICTIONS between sources
3. Highlight CONSENSUS points (claims supported by multiple sources)
4. Flag any GAPS in the research that need more investigation
5. Provide a brief SIGNIFICANCE assessment for each finding

Format your output as a structured analysis with clear section headers using markdown.
Be specific — cite source URLs when referencing claims.
Do NOT make up information that isn't in the provided research data."""


def analyst_node(state: ResearchState) -> dict:
    """
    Analyst agent node for the LangGraph pipeline.

    Takes raw research_data AND rag_context and produces a structured
    analysis with themes, contradictions, consensus, and gaps.
    """
    topic = state["topic"]
    research_data = state.get("research_data", [])
    rag_context = state.get("rag_context", [])

    if not research_data and not rag_context:
        return {
            "analysis": "⚠️ No research data available to analyze.",
            "messages": ["📊 Analyst: No data to analyze — skipping."],
            "current_agent": "analyst",
        }

    # Compile research data into a single text block
    compiled_data = "\n\n---\n\n".join(research_data)

    # Add RAG context if available
    rag_section = ""
    if rag_context:
        compiled_rag = "\n\n---\n\n".join(rag_context)
        rag_section = f"""

DOCUMENT CONTEXT (from uploaded files & past research):
{compiled_rag}"""

    analysis_prompt = f"""Analyze the following research data on the topic: "{topic}"

WEB RESEARCH DATA:
{compiled_data}
{rag_section}

Provide a comprehensive structured analysis following your guidelines.
When citing, distinguish between web sources and document sources."""

    response = llm.invoke([
        SystemMessage(content=ANALYST_SYSTEM_PROMPT),
        HumanMessage(content=analysis_prompt),
    ])

    analysis = response.content

    rag_note = f" + {len(rag_context)} document chunks" if rag_context else ""
    return {
        "analysis": analysis,
        "messages": [f"📊 Analyst: Analyzed {len(research_data)} web results{rag_note}"],
        "current_agent": "analyst",
    }

