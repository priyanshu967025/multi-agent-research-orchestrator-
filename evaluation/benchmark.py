"""
🎯 CLI Benchmark Script
───────────────────────
Usage:
    python -m evaluation.benchmark --topic "Autonomous AI Agents"
"""

import argparse
import json
import os
from evaluation.evaluator import BenchmarkEvaluator


def main():
    parser = argparse.ArgumentParser(description="Run Benchmark Evaluation (Multi-Agent vs Single-Agent)")
    parser.add_argument("--topic", type=str, default="Impact of Quantum Computing on Modern Cryptography", help="Research topic to benchmark")
    parser.add_argument("--output", type=str, default="benchmark_results.json", help="Path to save output JSON")
    args = parser.parse_args()

    evaluator = BenchmarkEvaluator()
    results = evaluator.run_benchmark(args.topic)

    print("\n" + "=" * 60)
    print("🏆 BENCHMARK EVALUATION RESULTS 🏆")
    print("=" * 60)
    print(f"Topic: {results['topic']}")
    print(f"Single-Agent Overall Score: {results['metrics_summary']['single_agent_score']}/10")
    print(f"Multi-Agent Overall Score:  {results['metrics_summary']['multi_agent_score']}/10")
    print(f"Quality Improvement:       +{results['metrics_summary']['quality_improvement_pct']}%")
    print(f"Single-Agent Citations:     {results['metrics_summary']['single_agent_citations']}")
    print(f"Multi-Agent Citations:      {results['metrics_summary']['multi_agent_citations']}")
    print(f"Winner:                     {results['evaluation'].get('winner', 'Multi-Agent Research Orchestrator')}")
    print("=" * 60)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Saved benchmark details to {args.output}")


if __name__ == "__main__":
    main()
