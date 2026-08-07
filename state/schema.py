from __future__ import annotations
import operator
from typing import Annotated, TypedDict

class ResearchState(TypedDict):
    topic: str

    research_data: Annotated[list[str], operator.add]
    rag_context: Annotated[list[str], operator.add]
    analysis: str
    fact_check_result: str
    fact_check_passed: bool
    revision_count: int
    final_report: str

    messages: Annotated[list[str], operator.add]
    current_agent: str
    error: str
