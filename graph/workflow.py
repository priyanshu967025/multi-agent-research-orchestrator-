from langgraph.graph import StateGraph, END
from state.schema import ResearchState
from agents.researcher import researcher_node
from agents.analyst import analyst_node
from agents.fact_checker import fact_checker_node
from agents.writer import writer_node

def should_continue(state: ResearchState) -> str:
    if state.get("fact_check_passed", True):
        return "writer"
    else:
        return "researcher"

def build_graph():
    workflow = StateGraph(ResearchState)

    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("writer", writer_node)

    workflow.set_entry_point("researcher")

    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "fact_checker")

    workflow.add_conditional_edges(
        "fact_checker",
        should_continue,
        {
            "writer": "writer",
            "researcher": "researcher",
        }
    )

    workflow.add_edge("writer", END)

    return workflow.compile()

research_graph = build_graph()
