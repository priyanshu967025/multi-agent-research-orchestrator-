"""Domain services for durable research execution.

Views create and authorize jobs; this module owns agent execution and persistence.
"""
from __future__ import annotations

import re
import threading
import time
from urllib.parse import urlparse

from django.db import close_old_connections, transaction
from django.utils import timezone

from .models import ResearchEvent, ResearchSession, ResearchSource


SOURCE_PATTERN = re.compile(r"^\[Source:\s*(?P<url>[^\]]+)\]\s*(?P<content>.*)$", re.DOTALL)
MAX_EVENT_MESSAGE_LENGTH = 1000
MAX_SOURCE_SNIPPET_LENGTH = 2000


def initial_research_state(topic: str) -> dict:
    return {
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


def queue_research_job(user, topic: str) -> ResearchSession:
    """Create a durable job and its first timeline event before any agent runs."""
    with transaction.atomic():
        session = ResearchSession.objects.create(
            user=user,
            topic=topic,
            status="queued",
            final_report="",
        )
        _record_event(session, "queued", "Research job created and waiting to start.")
    return session


def _record_event(session: ResearchSession, stage: str, message: object) -> None:
    next_sequence = session.progress_version + 1
    text = " ".join(str(message).split())[:MAX_EVENT_MESSAGE_LENGTH]
    ResearchEvent.objects.create(
        session=session,
        sequence=next_sequence,
        stage=stage,
        message=text,
    )
    ResearchSession.objects.filter(pk=session.pk).update(progress_version=next_sequence)
    session.progress_version = next_sequence


def _store_sources(session: ResearchSession, web_sources: list[str], rag_context: list[str]) -> None:
    ResearchSource.objects.filter(session=session).delete()
    sources: list[ResearchSource] = []
    for position, raw_source in enumerate(web_sources, start=1):
        match = SOURCE_PATTERN.match(raw_source)
        url = match.group("url").strip() if match else ""
        snippet = (match.group("content") if match else raw_source).strip()
        parsed = urlparse(url)
        sources.append(
            ResearchSource(
                session=session,
                source_type="web",
                position=position,
                url=url[:2048],
                title=parsed.netloc[:512],
                domain=parsed.netloc[:255],
                snippet=snippet[:MAX_SOURCE_SNIPPET_LENGTH],
            )
        )
    for position, snippet in enumerate(rag_context, start=1):
        sources.append(
            ResearchSource(
                session=session,
                source_type="rag",
                position=position,
                title="Uploaded knowledge base",
                snippet=str(snippet).strip()[:MAX_SOURCE_SNIPPET_LENGTH],
            )
        )
    ResearchSource.objects.bulk_create(sources)


def _run_graph(session: ResearchSession) -> dict:
    from graph.workflow import research_graph

    state = initial_research_state(session.topic)
    collected_web_sources: list[str] = []
    collected_rag_context: list[str] = []

    if not hasattr(research_graph, "stream"):
        return research_graph.invoke(state, {"recursion_limit": 25})

    for event in research_graph.stream(state, {"recursion_limit": 25}):
        for stage, output in event.items():
            if stage == "__end__":
                continue
            state.update(output)
            collected_web_sources.extend(output.get("research_data", []))
            collected_rag_context.extend(output.get("rag_context", []))
            messages = output.get("messages", [])
            _record_event(
                session,
                stage if stage in dict(ResearchEvent.STAGE_CHOICES) else "researcher",
                messages[-1] if messages else f"{stage.replace('_', ' ').title()} completed.",
            )

    state["research_data"] = collected_web_sources
    state["rag_context"] = collected_rag_context
    return state


def run_research_job(session_id: int) -> None:
    """Run a persisted job and always leave it in a terminal state."""
    close_old_connections()
    session = ResearchSession.objects.get(pk=session_id)
    started = time.monotonic()
    session.status = "running"
    session.started_at = timezone.now()
    session.error_code = ""
    session.error_message = ""
    session.save(update_fields=["status", "started_at", "error_code", "error_message"])
    _record_event(session, "researcher", "Research agents are gathering evidence.")

    try:
        result = _run_graph(session)
        web_sources = result.get("research_data", [])
        rag_context = result.get("rag_context", [])
        with transaction.atomic():
            _store_sources(session, web_sources, rag_context)
            session.status = "completed"
            session.final_report = result.get("final_report", "")
            session.fact_check_result = result.get("fact_check_result", "")
            session.web_sources_count = len(web_sources)
            session.rag_chunks_count = len(rag_context)
            session.revision_count = result.get("revision_count", 0)
            session.duration_seconds = round(time.monotonic() - started, 2)
            session.completed_at = timezone.now()
            session.save()
            _record_event(session, "completed", "Research report completed and saved.")
    except Exception:
        session.status = "failed"
        session.error_code = "research_execution_failed"
        session.error_message = "Research could not be completed. Please try again."
        session.duration_seconds = round(time.monotonic() - started, 2)
        session.completed_at = timezone.now()
        session.save()
        _record_event(session, "failed", session.error_message)
    finally:
        close_old_connections()


def launch_research_job(session_id: int, asynchronous: bool = True) -> None:
    """Start a local background run, or run inline for deterministic deployments/tests."""
    if asynchronous:
        thread = threading.Thread(target=run_research_job, args=(session_id,), daemon=True)
        thread.start()
        return
    run_research_job(session_id)
