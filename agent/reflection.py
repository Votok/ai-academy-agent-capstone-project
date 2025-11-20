"""
Self-reflection and critique capabilities
Agent evaluates its own outputs
"""
from typing import List, Optional
import json
from openai import OpenAI
from dataclasses import dataclass

from rag.config import OPENAI_API_KEY, AGENT_MODEL, MIN_CONFIDENCE_SCORE


@dataclass
class ReflectionResult:
    """Structured output for self-reflection"""
    confidence_score: float  # 0.0-1.0
    is_satisfactory: bool
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    missing_information: List[str]


class SelfReflectionCritic:
    """
    Critiques agent's own outputs
    Provides feedback for iterative improvement
    """

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def reflect(
        self,
        query: str,
        answer: str,
        retrieved_context: Optional[List[str]] = None
    ) -> ReflectionResult:
        """
        Perform self-reflection on generated answer using JSON mode
        """
        system_prompt = """You are a critical AI assistant that evaluates answer quality.

Assess the answer based on:
1. Accuracy - Is the information correct?
2. Completeness - Does it fully address the query?
3. Clarity - Is it well-explained?
4. Relevance - Does it stay on topic?
5. Evidence - Is it supported by the context?

Respond with a JSON object with these keys:
- confidence_score: float (0.0-1.0)
- is_satisfactory: boolean
- strengths: array of strings
- weaknesses: array of strings
- suggestions: array of strings
- missing_information: array of strings

Be honest and constructive. Identify both strengths and areas for improvement."""

        context_str = ""
        if retrieved_context:
            context_str = "\n\nRetrieved Context:\n" + "\n---\n".join(retrieved_context[:3])

        user_prompt = f"""Query: {query}

Answer: {answer}
{context_str}

Evaluate this answer critically."""

        response = self.client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent critique
            response_format={"type": "json_object"}
        )

        # Parse JSON response into dataclass
        result = json.loads(response.choices[0].message.content)
        return ReflectionResult(
            confidence_score=float(result.get("confidence_score", 0.5)),
            is_satisfactory=bool(result.get("is_satisfactory", False)),
            strengths=result.get("strengths", []),
            weaknesses=result.get("weaknesses", []),
            suggestions=result.get("suggestions", []),
            missing_information=result.get("missing_information", [])
        )

    def should_revise(self, reflection: ReflectionResult) -> bool:
        """
        Determine if answer should be revised based on reflection
        """
        # Revise if confidence is below threshold
        if reflection.confidence_score < MIN_CONFIDENCE_SCORE:
            return True

        # Revise if not satisfactory
        if not reflection.is_satisfactory:
            return True

        # Revise if there are critical weaknesses
        if len(reflection.weaknesses) > len(reflection.strengths):
            return True

        return False

    def generate_revision_prompt(
        self,
        original_query: str,
        original_answer: str,
        reflection: ReflectionResult
    ) -> str:
        """
        Generate a prompt for revising the answer based on reflection
        """
        revision_prompt = f"""Original Query: {original_query}

Previous Answer:
{original_answer}

Critique:
Confidence: {reflection.confidence_score:.2f}
Weaknesses: {', '.join(reflection.weaknesses)}
Missing Information: {', '.join(reflection.missing_information)}

Suggestions for improvement:
{chr(10).join(f"- {s}" for s in reflection.suggestions)}

Please provide an improved answer that addresses these issues."""

        return revision_prompt


# CLI for testing
if __name__ == "__main__":
    critic = SelfReflectionCritic()

    # Test reflection
    test_query = "What is RAG?"
    test_answer = "RAG is a technique that combines retrieval with generation."

    print("🤔 Reflecting on answer...")
    print(f"Query: {test_query}")
    print(f"Answer: {test_answer}\n")

    reflection = critic.reflect(test_query, test_answer)

    print(f"Confidence: {reflection.confidence_score:.2f}")
    print(f"Satisfactory: {reflection.is_satisfactory}")
    print(f"\nStrengths:")
    for s in reflection.strengths:
        print(f"  ✓ {s}")
    print(f"\nWeaknesses:")
    for w in reflection.weaknesses:
        print(f"  ✗ {w}")
    print(f"\nSuggestions:")
    for sg in reflection.suggestions:
        print(f"  → {sg}")

    if critic.should_revise(reflection):
        print("\n🔄 Answer should be revised")
        revision_prompt = critic.generate_revision_prompt(
            test_query, test_answer, reflection
        )
        print(f"\nRevision Prompt:\n{revision_prompt}")
