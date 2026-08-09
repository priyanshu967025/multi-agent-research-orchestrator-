"""
Shared state schema for the multi-agent research pipeline.

Uses TypedDict with Annotated reducer fields so that multiple agents
can safely append to list fields without overwriting each other.
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict


class ResearchState(TypedDict):
    """Central state shared across all agents in the research pipeline."""

    # ── User Input ────────────────────────────────────────────────────
    topic: str
    """The user's research query / topic."""

    # ── Researcher Output ─────────────────────────────────────────────
    research_data: Annotated[list[str], operator.add]
    """Raw search results collected by the Researcher agent.
    Uses operator.add reducer — each agent call *appends* to this list."""

    # ── Analyst Output ────────────────────────────────────────────────
    analysis: str
    """Structured analysis with key themes, patterns, and insights."""

    # ── Fact-Checker Output ───────────────────────────────────────────
    fact_check_result: str
    """Detailed fact-check report: verified claims, flagged issues."""

    fact_check_passed: bool
    """Gate flag — True means proceed to Writer, False routes back to Researcher."""

    revision_count: int
    """Number of research→fact-check loops completed. Capped at MAX_REVISIONS."""

    # ── Writer Output ─────────────────────────────────────────────────
    final_report: str
    """The polished, cited markdown report produced by the Writer."""

    # ── RAG Context ───────────────────────────────────────────────────
    rag_context: Annotated[list[str], operator.add]
    """Context retrieved from uploaded documents via ChromaDB RAG.
    Uses operator.add reducer — appended alongside web search results."""

    # ── Pipeline Metadata ─────────────────────────────────────────────
    messages: Annotated[list[str], operator.add]
    """Running log of agent activity messages for the UI.
    Uses operator.add reducer — agents append status messages here."""

    current_agent: str
    """Name of the currently active agent (for UI status display)."""

    error: str
    """Error message if something goes wrong during pipeline execution."""
