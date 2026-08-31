"""
Benchmark evaluator: Single-Agent Baseline vs Multi-Agent Orchestrator.

This module powers the ``POST /api/research/benchmark/`` endpoint. It provides:

- ``run_single_agent_baseline(topic)``: one LLM call, no fact-checking, no
  revision loop, no RAG — the naive baseline that the multi-agent pipeline is
  compared against.
- ``evaluate_outputs(topic, single_agent_text, multi_agent_text)``: scores
  both reports on depth and verifiability (0-10) and emits a verdict.
"""
import re

from config.providers import get_llm_with_fallback

SINGLE_AGENT_PROMPT = """You are an expert research analyst.
Write a comprehensive, detailed Markdown research report about the topic below.
Cover market overview, technical details, key players, challenges, and future outlook.
Include section headings and cite sources inline wherever possible.

TOPIC: {topic}"""

JUDGE_PROMPT = """You are a strict research-quality judge.
Compare the SINGLE-AGENT report (one LLM call) against the MULTI-AGENT report
(4-agent pipeline: Researcher -> Analyst -> Fact Checker -> Writer with a revision loop).

Score BOTH reports from 0 to 10 on:
- depth_score: depth, structure, coverage of multiple angles.
- verifiability_score: how well claims are grounded in sources/citations.

Return ONLY valid JSON, no markdown fences, in this exact shape:
{{"single_agent": {{"depth_score": 0, "verifiability_score": 0}},
 "multi_agent": {{"depth_score": 0, "verifiability_score": 0}},
 "verdict": "MULTI_AGENT_SUPERIOR"}}

verdict must be one of: MULTI_AGENT_SUPERIOR, COMPARABLE, SINGLE_AGENT_SUPERIOR.

SINGLE-AGENT REPORT:
{single_report}

MULTI-AGENT REPORT:
{multi_report}"""


def run_single_agent_baseline(topic: str) -> dict:
    """
    Runs the naive single-agent baseline: one LLM call that tries to do
    everything at once (search knowledge + write report) with no verification.

    Returns a dict containing the generated report under the key ``text``.
    """
    report = f"# Research Report: {topic}\n\n*Single-agent baseline generated with available data.*"

    try:
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = get_llm_with_fallback(model=None, temperature=0.5)
        response = llm.invoke([
            SystemMessage(content=SINGLE_AGENT_PROMPT.format(topic=topic)),
            HumanMessage(content=f"Write the report on: {topic}"),
        ])
        report = response.content
    except Exception as e:
        print(f"[benchmark] Single-agent baseline fallback: {e}")

    return {"text": report, "topic": topic}


# ---------------------------------------------------------------------------
# Heuristic scoring (always available; LLM judge augments when a key exists)
# ---------------------------------------------------------------------------

def _clamp(value: int) -> int:
    return max(0, min(10, int(value)))


def _depth_score(text: str) -> int:
    """Depth heuristic: section coverage, bullet density and length."""
    if not text:
        return 0
    headings = len(re.findall(r"^#{1,4}\s.+$", text, flags=re.MULTILINE))
    bullets = len(re.findall(r"^\s*[-*+]\s", text, flags=re.MULTILINE))
    words = len(text.split())
    score = min(headings, 8) + min(bullets // 4, 4) + min(words // 150, 3)
    return _clamp(score)


def _verifiability_score(text: str) -> int:
    """Verifiability heuristic: citations, URLs and explicit source markers."""
    if not text:
        return 0
    urls = len(re.findall(r"https?://\S+", text))
    citations = len(re.findall(r"\[\d+\]|\[Source[:\]]|\(Source[:\s]", text, flags=re.IGNORECASE))
    score = min(urls, 5) * 1.5 + min(citations, 5)
    return _clamp(score)


def _heuristic_metrics(single_text: str, multi_text: str) -> dict:
    return {
        "single_agent": {
            "depth_score": _depth_score(single_text),
            "verifiability_score": _verifiability_score(single_text),
        },
        "multi_agent": {
            "depth_score": _depth_score(multi_text),
            "verifiability_score": _verifiability_score(multi_text),
        },
    }


def _heuristic_verdict(metrics: dict) -> str:
    single_total = metrics["single_agent"]["depth_score"] + metrics["single_agent"]["verifiability_score"]
    multi_total = metrics["multi_agent"]["depth_score"] + metrics["multi_agent"]["verifiability_score"]
    if multi_total - single_total >= 3:
        return "MULTI_AGENT_SUPERIOR"
    if single_total - multi_total >= 3:
        return "SINGLE_AGENT_SUPERIOR"
    return "COMPARABLE"


def evaluate_outputs(topic: str, single_agent_text: str, multi_agent_text: str) -> dict:
    """
    Scores the single-agent baseline and the multi-agent pipeline report and
    returns comparison metrics plus a verdict.

    Returns:
        {
          "single_agent": {"depth_score": int, "verifiability_score": int},
          "multi_agent":  {"depth_score": int, "verifiability_score": int},
          "verdict": "MULTI_AGENT_SUPERIOR" | "COMPARABLE" | "SINGLE_AGENT_SUPERIOR",
        }
    """
    metrics = _heuristic_metrics(single_agent_text, multi_agent_text)

    # LLM-as-a-judge for richer evaluation when a provider is available.
    try:
        import json

        from langchain_core.messages import SystemMessage, HumanMessage

        llm = get_llm_with_fallback(model=None, temperature=0.0)
        response = llm.invoke([
            SystemMessage(content="You are a strict JSON-only research quality judge."),
            HumanMessage(content=JUDGE_PROMPT.format(
                topic=topic,
                single_report=single_agent_text[:8000],
                multi_report=multi_agent_text[:8000],
            )),
        ])
        parsed = json.loads(response.content.strip())
        metrics = {
            "single_agent": {
                "depth_score": _clamp(parsed["single_agent"]["depth_score"]),
                "verifiability_score": _clamp(parsed["single_agent"]["verifiability_score"]),
            },
            "multi_agent": {
                "depth_score": _clamp(parsed["multi_agent"]["depth_score"]),
                "verifiability_score": _clamp(parsed["multi_agent"]["verifiability_score"]),
            },
        }
        verdict = parsed.get("verdict", _heuristic_verdict(metrics))
    except Exception as e:
        print(f"[benchmark] LLM judge fallback to heuristics: {e}")
        verdict = _heuristic_verdict(metrics)

    metrics["verdict"] = verdict
    return metrics
