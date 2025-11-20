"""
Prompts for agent reasoning, reflection, and revision
"""
from typing import List

AGENT_SYSTEM_PROMPT = """You are an intelligent AI agent with access to a knowledge base about AI Academy course materials.

Your capabilities:
- Retrieve relevant information from the knowledge base
- Break down complex questions into steps
- Use tools when needed (calculations, formatting, etc.)
- Reflect on your answers and improve them

Your approach:
1. Understand the query carefully
2. Retrieve relevant context
3. Generate a thoughtful answer
4. Reflect on quality
5. Revise if needed

Be accurate, clear, and helpful."""


ANSWER_GENERATION_PROMPT = """Based on the retrieved context below, answer the user's query.

Query: {query}

Retrieved Context:
{context}

Your task:
1. Synthesize the information from the context
2. Answer the query directly and clearly
3. Cite sources when relevant
4. If information is insufficient, say so

Answer:"""


REVISION_PROMPT = """You previously answered a query, but reflection identified areas for improvement.

Original Query: {query}

Previous Answer:
{previous_answer}

Reflection Feedback:
{feedback}

Retrieved Context (may include new information):
{context}

Provide an improved answer that addresses the feedback:"""


def format_answer_prompt(query: str, context: List[str]) -> str:
    """Format prompt for answer generation"""
    context_str = "\n\n---\n\n".join(context)
    return ANSWER_GENERATION_PROMPT.format(
        query=query,
        context=context_str
    )


def format_revision_prompt(
    query: str,
    previous_answer: str,
    feedback: str,
    context: List[str]
) -> str:
    """Format prompt for answer revision"""
    context_str = "\n\n---\n\n".join(context)
    return REVISION_PROMPT.format(
        query=query,
        previous_answer=previous_answer,
        feedback=feedback,
        context=context_str
    )
