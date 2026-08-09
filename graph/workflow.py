"""
🔗 LangGraph Workflow
─────────────────────
Wires the 4 agents into a StateGraph pipeline with a conditional
feedback loop: Researcher → Analyst → Fact-Checker → Writer,
where the Fact-Checker can route back to the Researcher if claims
are unverifiable (up to MAX_REVISIONS times).
"""

from langgraph.graph import StateGraph, END

from state.schema import ResearchState
from agents.researcher import researcher_node
from agents.analyst import analyst_node
from agents.fact_checker import fact_checker_node
from agents.writer import writer_node


def should_continue(state: ResearchState) -> str:
    """
    Conditional edge after the Fact-Checker node.

    Routes to:
    - "writer"      → if fact-check passed
    - "researcher"  → if fact-check failed and revisions remain
    """
    if state.get("fact_check_passed", True):
        return "writer"
    else:
        return "researcher"


def build_graph() -> StateGraph:
    """
    Build and compile the research orchestrator graph.

    Pipeline: researcher → analyst → fact_checker → (writer | researcher)

    Returns:
        Compiled LangGraph StateGraph ready for invocation.
    """
    # Create the graph with our shared state schema
    workflow = StateGraph(ResearchState)

    # ── Register nodes ────────────────────────────────────────────────
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("writer", writer_node)

    # ── Define edges (pipeline flow) ──────────────────────────────────
    workflow.set_entry_point("researcher")

    # Sequential: researcher → analyst → fact_checker
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "fact_checker")

    # Conditional: fact_checker → writer OR → researcher (feedback loop)
    workflow.add_conditional_edges(
        "fact_checker",
        should_continue,
        {
            "writer": "writer",
            "researcher": "researcher",
        },
    )

    # Terminal: writer → END
    workflow.add_edge("writer", END)

    # ── Compile and return ────────────────────────────────────────────
    graph = workflow.compile()
    return graph


# Pre-built graph instance for import
research_graph = build_graph()


def run_research_workflow(topic: str) -> dict:
    """
    Convenience function to execute the full multi-agent research workflow on a topic.
    
    Args:
        topic: The research topic string.
        
    Returns:
        Final ResearchState dictionary containing final_report, messages, revision_count, etc.
    """
    initial_state = {
        "topic": topic,
        "research_data": [],
        "analysis": "",
        "fact_check_result": "",
        "fact_check_passed": False,
        "revision_count": 0,
        "final_report": "",
        "rag_context": [],
        "messages": [],
        "current_agent": "",
        "error": "",
    }
    final_state = research_graph.invoke(initial_state, {"recursion_limit": 25})
    return final_state

