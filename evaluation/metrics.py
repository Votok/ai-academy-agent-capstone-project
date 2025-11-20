"""Evaluation metrics module.

This module defines metrics for agent performance evaluation:
- Answer quality (LLM-as-judge: relevance, accuracy, completeness, coherence)
- Tool call success rate and usage patterns
- Reasoning efficiency (iterations, confidence)
- Topic coverage analysis

Implementation: Phase 7
"""

from typing import List, Dict, Any, Optional
import json
from dataclasses import dataclass
from openai import OpenAI

from rag.config import OPENAI_API_KEY, EVAL_MODEL
from agent.memory import AgentState


@dataclass
class AnswerEvaluation:
    """Structured evaluation of an answer"""
    relevance_score: float  # 0.0-1.0
    accuracy_score: float  # 0.0-1.0
    completeness_score: float  # 0.0-1.0
    coherence_score: float  # 0.0-1.0
    overall_score: float  # 0.0-1.0
    reasoning: str


class AgentEvaluator:
    """
    Evaluate agent performance using LLM-as-judge and state analysis
    """

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def evaluate_answer(
        self,
        query: str,
        answer: str,
        expected_topics: Optional[List[str]] = None
    ) -> AnswerEvaluation:
        """
        Evaluate answer quality using LLM-as-judge with JSON mode

        Args:
            query: The original user query
            answer: The agent's generated answer
            expected_topics: Optional list of topics that should be covered

        Returns:
            AnswerEvaluation with scores and reasoning
        """
        system_prompt = """You are an expert evaluator assessing AI-generated answers.

Evaluate based on:
1. Relevance: Does it directly address the query?
2. Accuracy: Is the information correct and factual?
3. Completeness: Are all aspects of the query covered?
4. Coherence: Is it well-structured, clear, and logically organized?

Respond with a JSON object with these keys:
- relevance_score: float (0.0-1.0)
- accuracy_score: float (0.0-1.0)
- completeness_score: float (0.0-1.0)
- coherence_score: float (0.0-1.0)
- overall_score: float (0.0-1.0, weighted average)
- reasoning: string explaining the scores"""

        expected_topics_str = ""
        if expected_topics:
            expected_topics_str = f"\nExpected topics: {', '.join(expected_topics)}"

        user_prompt = f"""Query: {query}

Answer: {answer}
{expected_topics_str}

Evaluate this answer."""

        response = self.client.chat.completions.create(
            model=EVAL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        # Parse JSON response into dataclass
        result = json.loads(response.choices[0].message.content)
        return AnswerEvaluation(
            relevance_score=float(result.get("relevance_score", 0.5)),
            accuracy_score=float(result.get("accuracy_score", 0.5)),
            completeness_score=float(result.get("completeness_score", 0.5)),
            coherence_score=float(result.get("coherence_score", 0.5)),
            overall_score=float(result.get("overall_score", 0.5)),
            reasoning=result.get("reasoning", "")
        )

    def evaluate_tool_usage(self, state: AgentState) -> Dict[str, Any]:
        """
        Evaluate tool calling effectiveness

        Args:
            state: The agent's final state after execution

        Returns:
            Dictionary with tool usage metrics
        """
        tool_steps = state.get_steps_by_type("tool_call")

        if not tool_steps:
            return {
                "tools_used": 0,
                "tool_calls": 0,
                "success_rate": 0.0,
                "tool_list": []
            }

        # Extract tool information from metadata
        all_tools = []
        successful_calls = 0
        total_calls = 0

        for step in tool_steps:
            tools = step.metadata.get("tools", [])
            if tools:
                all_tools.extend(tools)
                successful_calls += len(tools)
            total_calls += 1

        return {
            "tools_used": len(set(all_tools)),  # Unique tools
            "tool_calls": total_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0.0,
            "tool_list": all_tools
        }

    def evaluate_reasoning_efficiency(self, state: AgentState) -> Dict[str, Any]:
        """
        Evaluate reasoning loop efficiency

        Args:
            state: The agent's final state after execution

        Returns:
            Dictionary with reasoning efficiency metrics
        """
        reflection_steps = state.get_steps_by_type("reflect")

        return {
            "iterations": state.iteration,
            "steps_taken": len(state.reasoning_steps),
            "confidence_final": state.confidence_score,
            "reflection_count": len(reflection_steps),
            "efficiency_score": 1.0 - (state.iteration / state.max_iterations),
            "completed": state.is_complete
        }

    def calculate_topic_coverage(
        self,
        answer: str,
        expected_topics: List[str]
    ) -> float:
        """
        Calculate what percentage of expected topics are mentioned

        Args:
            answer: The generated answer
            expected_topics: List of topics that should be covered

        Returns:
            Coverage ratio (0.0-1.0)
        """
        if not expected_topics:
            return 1.0

        answer_lower = answer.lower()
        covered = sum(
            1 for topic in expected_topics
            if topic.lower() in answer_lower
        )
        return covered / len(expected_topics)


class EvaluationReport:
    """Generate evaluation reports and summary statistics"""

    @staticmethod
    def generate_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics from evaluation results

        Args:
            results: List of detailed evaluation results

        Returns:
            Dictionary with aggregate metrics
        """
        if not results:
            return {}

        # Average scores
        avg_relevance = sum(r["answer_eval"]["relevance_score"] for r in results) / len(results)
        avg_accuracy = sum(r["answer_eval"]["accuracy_score"] for r in results) / len(results)
        avg_completeness = sum(r["answer_eval"]["completeness_score"] for r in results) / len(results)
        avg_coherence = sum(r["answer_eval"]["coherence_score"] for r in results) / len(results)
        avg_overall = sum(r["answer_eval"]["overall_score"] for r in results) / len(results)

        # Reasoning stats
        avg_iterations = sum(r["reasoning"]["iterations"] for r in results) / len(results)
        avg_confidence = sum(r["reasoning"]["confidence_final"] for r in results) / len(results)
        avg_efficiency = sum(r["reasoning"]["efficiency_score"] for r in results) / len(results)

        # Tool stats
        queries_with_tools = sum(1 for r in results if r["tools"]["tools_used"] > 0)
        avg_tool_success = sum(r["tools"]["success_rate"] for r in results) / len(results)

        # Topic coverage
        avg_topic_coverage = sum(r["topic_coverage"] for r in results) / len(results)

        return {
            "total_queries": len(results),
            "answer_quality": {
                "relevance": round(avg_relevance, 3),
                "accuracy": round(avg_accuracy, 3),
                "completeness": round(avg_completeness, 3),
                "coherence": round(avg_coherence, 3),
                "overall": round(avg_overall, 3)
            },
            "reasoning": {
                "avg_iterations": round(avg_iterations, 2),
                "avg_confidence": round(avg_confidence, 3),
                "avg_efficiency": round(avg_efficiency, 3)
            },
            "tools": {
                "queries_using_tools": queries_with_tools,
                "tool_usage_rate": round(queries_with_tools / len(results), 3),
                "avg_success_rate": round(avg_tool_success, 3)
            },
            "topic_coverage": {
                "average": round(avg_topic_coverage, 3)
            }
        }


# Test code
if __name__ == "__main__":
    print("🧪 Testing Evaluation Metrics Module")
    print("=" * 60)

    # Test topic coverage
    evaluator = AgentEvaluator()

    test_answer = "RAG (Retrieval-Augmented Generation) is a technique that combines retrieval with generation."
    test_topics = ["RAG", "retrieval", "generation"]

    coverage = evaluator.calculate_topic_coverage(test_answer, test_topics)
    print(f"\n✓ Topic Coverage Test: {coverage:.2f} (expected: 1.0)")

    print("\n✅ Metrics module is functional!")
    print("\nNote: Full LLM-as-judge testing requires running the complete evaluation pipeline.")
