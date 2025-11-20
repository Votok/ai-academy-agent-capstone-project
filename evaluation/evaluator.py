"""Evaluation runner module.

This module orchestrates agent evaluation:
- Load test queries from JSON dataset
- Run AgentOrchestrator on each query
- Compute metrics (answer quality, reasoning, tools)
- Generate detailed per-query reports
- Create aggregate summary statistics
- Save results to evaluation/reports/

Implementation: Phase 7
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from agent.orchestrator import AgentOrchestrator
from evaluation.metrics import AgentEvaluator, EvaluationReport
from rag.config import EVAL_DATASET


class EvaluationRunner:
    """
    Run evaluation on test query dataset
    """

    def __init__(self, test_queries_path: str = None):
        """
        Initialize evaluation runner

        Args:
            test_queries_path: Path to test queries JSON file
        """
        self.test_queries_path = test_queries_path or str(EVAL_DATASET)
        self.orchestrator = AgentOrchestrator()
        self.evaluator = AgentEvaluator()

    def load_test_queries(self) -> List[Dict[str, Any]]:
        """
        Load test queries from JSON

        Returns:
            List of test query dictionaries
        """
        with open(self.test_queries_path, 'r') as f:
            data = json.load(f)
        return data["test_queries"]

    def run_evaluation(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Run evaluation on all test queries

        Args:
            verbose: Whether to show verbose output during execution

        Returns:
            Dictionary with evaluation results and summary
        """
        test_queries = self.load_test_queries()
        results = []

        print(f"🧪 Running evaluation on {len(test_queries)} queries...")
        print("=" * 60)

        for i, test_query in enumerate(test_queries, 1):
            query = test_query["query"]
            expected_topics = test_query.get("expected_topics", [])
            query_id = test_query["id"]

            print(f"\n[{i}/{len(test_queries)}] {query_id}: {query[:60]}...")

            # Run agent orchestrator
            state = self.orchestrator.run(query, verbose=False)

            # Evaluate answer quality (LLM-as-judge)
            answer_eval = self.evaluator.evaluate_answer(
                query=query,
                answer=state.current_answer,
                expected_topics=expected_topics
            )

            # Evaluate tool usage
            tool_eval = self.evaluator.evaluate_tool_usage(state)

            # Evaluate reasoning efficiency
            reasoning_eval = self.evaluator.evaluate_reasoning_efficiency(state)

            # Calculate topic coverage
            topic_coverage = self.evaluator.calculate_topic_coverage(
                state.current_answer,
                expected_topics
            )

            # Compile result
            result = {
                "query_id": query_id,
                "query": query,
                "category": test_query.get("category", "unknown"),
                "difficulty": test_query.get("difficulty", "unknown"),
                "requires_tools": test_query.get("requires_tools", False),
                "answer": state.current_answer,
                "answer_eval": {
                    "relevance_score": answer_eval.relevance_score,
                    "accuracy_score": answer_eval.accuracy_score,
                    "completeness_score": answer_eval.completeness_score,
                    "coherence_score": answer_eval.coherence_score,
                    "overall_score": answer_eval.overall_score,
                    "reasoning": answer_eval.reasoning
                },
                "topic_coverage": topic_coverage,
                "tools": tool_eval,
                "reasoning": reasoning_eval
            }

            results.append(result)

            # Print summary for this query
            print(f"  Overall: {answer_eval.overall_score:.2f} | "
                  f"Confidence: {state.confidence_score:.2f} | "
                  f"Iterations: {state.iteration} | "
                  f"Topics: {topic_coverage:.2f}")

        # Generate summary statistics
        summary = EvaluationReport.generate_summary(results)

        evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(test_queries),
            "summary": summary,
            "detailed_results": results
        }

        return evaluation_results

    def save_results(
        self,
        results: Dict[str, Any],
        output_path: str = None
    ) -> str:
        """
        Save evaluation results to file

        Args:
            results: Evaluation results dictionary
            output_path: Optional custom output path

        Returns:
            Path where results were saved
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"evaluation/reports/eval_{timestamp}.json"

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save JSON with indentation
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to {output_path}")
        return output_path


# CLI for running evaluation
if __name__ == "__main__":
    runner = EvaluationRunner()

    print("🧪 Starting Agent Evaluation\n")

    # Run evaluation
    results = runner.run_evaluation(verbose=False)

    # Display summary
    print("\n" + "=" * 60)
    print("📊 EVALUATION SUMMARY")
    print("=" * 60)

    summary = results["summary"]

    print(f"\nTotal Queries: {summary['total_queries']}")

    print(f"\n📝 Answer Quality:")
    for metric, score in summary["answer_quality"].items():
        print(f"  {metric.capitalize()}: {score:.3f}")

    print(f"\n🧠 Reasoning:")
    print(f"  Avg Iterations: {summary['reasoning']['avg_iterations']:.2f}")
    print(f"  Avg Confidence: {summary['reasoning']['avg_confidence']:.3f}")
    print(f"  Avg Efficiency: {summary['reasoning']['avg_efficiency']:.3f}")

    print(f"\n🔧 Tool Usage:")
    print(f"  Queries using tools: {summary['tools']['queries_using_tools']}")
    print(f"  Tool usage rate: {summary['tools']['tool_usage_rate']:.3f}")
    print(f"  Avg success rate: {summary['tools']['avg_success_rate']:.3f}")

    print(f"\n📚 Topic Coverage:")
    print(f"  Average: {summary['topic_coverage']['average']:.3f}")

    # Save results
    runner.save_results(results)

    print("\n✅ Evaluation complete!")
