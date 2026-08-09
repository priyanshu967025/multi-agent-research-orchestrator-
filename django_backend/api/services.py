"""
Service Layer Abstraction for Multi-Agent Research Orchestrator.
Decouples REST API views from LangGraph workflow and Benchmark engine.
"""

import time
from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from .models import ResearchTask, BenchmarkResult
from graph.workflow import run_research_workflow
from evaluation.evaluator import BenchmarkEvaluator


class ResearchOrchestratorService:
    """Service handling orchestration task execution and history recording."""

    @staticmethod
    def execute_research_task(topic: str, user: Optional[User] = None) -> ResearchTask:
        """
        Creates a ResearchTask record, executes the LangGraph workflow, 
        and updates the task status and results.
        """
        task = ResearchTask.objects.create(
            topic=topic,
            user=user,
            status='RUNNING'
        )

        start_time = time.time()
        try:
            workflow_output = run_research_workflow(topic)
            elapsed_time = round(time.time() - start_time, 2)

            task.status = 'COMPLETED'
            task.final_report = workflow_output.get("final_report", "No report generated.")
            task.revision_count = workflow_output.get("revision_count", 0)
            task.latency_seconds = elapsed_time
            task.save()
        except Exception as e:
            task.status = 'FAILED'
            task.error_message = str(e)
            task.latency_seconds = round(time.time() - start_time, 2)
            task.save()

        return task


class EvaluationBenchmarkService:
    """Service handling side-by-side LLM benchmark evaluation."""

    @staticmethod
    def run_benchmark_evaluation(topic: str, user: Optional[User] = None) -> BenchmarkResult:
        """
        Runs BenchmarkEvaluator on the given topic and saves results to DB.
        """
        evaluator = BenchmarkEvaluator()
        results = evaluator.run_benchmark(topic)

        metrics = results.get("metrics_summary", {})
        evaluation = results.get("evaluation", {})

        bench_obj = BenchmarkResult.objects.create(
            user=user,
            topic=topic,
            single_agent_score=metrics.get("single_agent_score", 0.0),
            multi_agent_score=metrics.get("multi_agent_score", 0.0),
            quality_improvement_pct=metrics.get("quality_improvement_pct", 0.0),
            winner=evaluation.get("winner", "Multi-Agent Research Orchestrator"),
            full_results_json=results
        )

        return bench_obj
