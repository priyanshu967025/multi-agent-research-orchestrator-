"""Shared pytest fixtures for the Django backend test suite."""
import sys
from pathlib import Path

# Project root — contains the `graph`, `benchmark`, `rag`, `state`, `config` packages.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest


@pytest.fixture(autouse=True)
def fast_password_hasher(settings):
    """Use fast MD5 password hasher during tests for rapid execution."""
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture(autouse=True)
def mock_embeddings(monkeypatch):
    """Stub HuggingFace embeddings so tests never load the PyTorch model or make network calls."""
    import rag.vector_store

    class FakeEmbeddings:
        def embed_documents(self, texts):
            return [[0.0] * 384 for _ in texts]

        def embed_query(self, text):
            return [0.0] * 384

    monkeypatch.setattr(rag.vector_store, "get_embeddings", lambda: FakeEmbeddings())


@pytest.fixture
def research_state():
    """Canned LangGraph state returned by the stubbed research graph."""
    return {
        "topic": "test topic",
        "research_data": [
            "[Source: https://example.com/1] Content from the first source.",
            "[Source: https://example.com/2] Content from the second source.",
        ],
        "rag_context": ["Retrieved chunk from an uploaded document."],
        "analysis": "## Key Themes\n- Solid electrolytes are the core innovation.",
        "fact_check_result": "VERDICT: PASSED",
        "fact_check_passed": True,
        "revision_count": 0,
        "final_report": "# Research Report: test topic\n\n## Executive Summary\nSummary of findings.",
        "messages": [
            "🔍 Researcher done",
            "📊 Analyst done",
            "✅ Fact-check PASSED",
            "✍️ Report complete",
        ],
        "current_agent": "writer",
        "error": "",
    }


@pytest.fixture
def mock_research_graph(monkeypatch, research_state):
    """Replace the compiled LangGraph with a stub whose invoke() returns canned state."""
    import graph.workflow

    class FakeGraph:
        def invoke(self, state, config=None):
            return dict(research_state)

    monkeypatch.setattr(graph.workflow, "research_graph", FakeGraph())
    return FakeGraph()


@pytest.fixture
def exploding_research_graph(monkeypatch):
    """Replace the research graph with one that raises — exercises the error path."""
    import graph.workflow

    class ExplodingGraph:
        def invoke(self, state, config=None):
            raise RuntimeError("pipeline exploded")

    monkeypatch.setattr(graph.workflow, "research_graph", ExplodingGraph())
    return ExplodingGraph()


@pytest.fixture(autouse=True)
def mock_llm_providers(monkeypatch):
    """Stub the LLM provider so tests never call a real API."""
    import config.providers

    class FakeLLM:
        def invoke(self, messages, **kwargs):
            from langchain_core.messages import AIMessage
            # Return appropriate canned responses based on context
            content = "\n".join(m.content for m in messages if hasattr(m, "content"))
            if "fact.check" in content.lower() or "verify" in content.lower():
                return AIMessage(content="VERDICT: PASSED")
            return AIMessage(content="# Canned Response\nThis is a stubbed LLM response for testing.")

    def fake_get_llm(*args, **kwargs):
        return FakeLLM()

    monkeypatch.setattr(config.providers, "get_llm_with_fallback", fake_get_llm)
    monkeypatch.setattr(config.providers, "get_llm", fake_get_llm)


@pytest.fixture
def mock_benchmark(monkeypatch):
    """Stub benchmark.evaluator so the endpoint never calls the LLM or pipeline."""
    import benchmark.evaluator

    baseline = {"text": "# Single-agent baseline\n\n## Overview\nBaseline content.", "topic": "any"}
    metrics = {
        "single_agent": {"depth_score": 5, "verifiability_score": 4},
        "multi_agent": {"depth_score": 9, "verifiability_score": 8},
        "verdict": "MULTI_AGENT_SUPERIOR",
    }
    monkeypatch.setattr(
        benchmark.evaluator,
        "run_single_agent_baseline",
        lambda topic: dict(baseline, topic=topic),
    )
    monkeypatch.setattr(
        benchmark.evaluator,
        "evaluate_outputs",
        lambda topic, single_agent_text, multi_agent_text: metrics,
    )
    return {"baseline": baseline, "metrics": metrics}
