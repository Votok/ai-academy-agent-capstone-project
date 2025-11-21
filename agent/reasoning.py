"""
Agent reasoning and planning capabilities
"""
from typing import List, Dict, Any
import json
from openai import OpenAI
from dataclasses import dataclass

from rag.config import OPENAI_API_KEY, AGENT_MODEL, AGENT_TEMPERATURE


@dataclass
class TaskDecomposition:
    """Structured output for task decomposition"""
    main_goal: str
    sub_tasks: List[str]
    required_information: List[str]
    complexity: str  # "simple", "moderate", or "complex"


class ReasoningPlanner:
    """
    Plans how to approach a query
    Decomposes complex queries into sub-tasks
    """

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def plan(self, query: str) -> TaskDecomposition:
        """
        Create a plan for answering the query using JSON mode
        """
        system_prompt = """You are an AI planning assistant. Given a user query, decompose it into a structured plan.

Analyze:
1. What is the main goal?
2. What sub-tasks are needed?
3. What information must be retrieved?
4. How complex is this query? (simple, moderate, or complex)

Respond with a JSON object with these keys:
- main_goal: string
- sub_tasks: array of strings
- required_information: array of strings
- complexity: string ("simple", "moderate", or "complex")

Be specific and actionable."""

        response = self.client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=AGENT_TEMPERATURE,
            response_format={"type": "json_object"}
        )

        # Parse JSON response into dataclass
        result = json.loads(response.choices[0].message.content)
        return TaskDecomposition(
            main_goal=result["main_goal"],
            sub_tasks=result["sub_tasks"],
            required_information=result["required_information"],
            complexity=result["complexity"]
        )

    def should_use_tools(self, query: str) -> bool:
        """
        Determine if query requires tool calling
        """
        tool_keywords = [
            "calculate", "compute", "math",
            "search", "find", "lookup",
            "date", "time", "today",
            "format", "table", "list"
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in tool_keywords)

    def identify_collections(self, query: str) -> List[str]:
        """
        Identify which collections to search based on query
        """
        collections = []

        query_lower = query.lower()

        # Check for AI Academy/course indicators
        if any(word in query_lower for word in [
            "academy", "course", "lesson", "week", "homework", "lecture", "material"
        ]):
            collections.append("ai_academy_course")

        # Check for transcript indicators
        if any(word in query_lower for word in [
            "video", "transcript", "lecture", "recording"
        ]):
            collections.append("transcripts")

        # Default to ai_academy_course if unclear
        if not collections:
            collections = ["ai_academy_course"]

        return collections


# CLI for testing
if __name__ == "__main__":
    planner = ReasoningPlanner()

    test_query = "What did I learn about RAG in week 3 of the AI Academy course?"

    print("🧠 Planning Query:")
    print(f"  {test_query}\n")

    plan = planner.plan(test_query)
    print(f"Main Goal: {plan.main_goal}")
    print(f"Complexity: {plan.complexity}")
    print(f"Sub-tasks:")
    for i, task in enumerate(plan.sub_tasks, 1):
        print(f"  {i}. {task}")
    print(f"Required Information:")
    for info in plan.required_information:
        print(f"  - {info}")
