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
3. Generate a thoughtful answer with proper citations
4. Reflect on quality
5. Revise if needed

IMPORTANT: Always cite your sources with document names and page numbers. This builds trust and allows verification."""


ANSWER_GENERATION_PROMPT = """Based on the retrieved context below, answer the user's query.

Query: {query}

Retrieved Context:
{context}

Your task:
1. Synthesize the information from the context
2. Answer the query directly and clearly
3. **ALWAYS cite sources** - include document name and page number for EVERY claim
4. Use direct quotes when appropriate (with quotation marks)
5. If information is insufficient, say so

CITATION FORMAT:
- For facts: "According to [document.pdf, page X], ..."
- For direct quotes: "As stated in [document.pdf, page X]: 'quote here'"
- For multiple sources: "This is supported by [doc1.pdf, page X] and [doc2.pdf, page Y]"

EXAMPLE:
"Retrieval-augmented generation (RAG) is a technique that enhances language models by retrieving relevant information from external sources [rag-intro.pdf, page 3]. As explained in [week2-embeddings.pdf, page 5]: 'RAG combines the strengths of retrieval systems and generative models.'"

Remember: Each chunk header shows [Chunk X from source, page Y] - use this information to cite properly.

Answer:"""


REVISION_PROMPT = """You previously answered a query, but reflection identified areas for improvement.

Original Query: {query}

Previous Answer:
{previous_answer}

Reflection Feedback:
{feedback}

Retrieved Context (may include new information):
{context}

Provide an improved answer that addresses the feedback.

IMPORTANT REMINDERS:
- ALWAYS cite sources with document names and page numbers
- Use format: [document.pdf, page X]
- Include direct quotes when appropriate
- Ensure every major claim has a citation

Improved Answer:"""


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


# LinkedIn Post Template

LINKEDIN_POST_TEMPLATE = """Excited to share that I've completed the Ciklum AI Academy - Engineering Learning Path! 🎓

This intensive program was specifically designed for developers and architects wanting to dive deep into the technical foundations of AI systems. Through mentor-led sessions and challenging practical assignments, I built a complete autonomous agentic AI system from the ground up.

What I built:
• RAG architecture with vector search and embeddings
• Self-reflection loops that critique and improve outputs
• Intelligent tool-calling for autonomous actions
• Multi-step reasoning and planning capabilities

The hands-on experience taught me to tackle complex real-world AI challenges, automate sophisticated tasks, and work with cutting-edge methods. I'm energized by the technical depth I've gained and ready to bring these skills to production systems.

The AI landscape is evolving rapidly, and I'm equipped with both the technical skills and adaptability to stay ahead of the curve. Looking forward to what's next! {custom_closing}

Learn more about Ciklum's AI initiatives: https://www.ciklum.com/

#Ciklum #AIAcademy #MachineLearning #ArtificialIntelligence #EngineeringPath"""


def format_linkedin_post(custom_closing: str = "") -> str:
    """
    Format LinkedIn post about Ciklum AI Academy completion

    Args:
        custom_closing: Optional custom closing statement

    Returns:
        Formatted LinkedIn post text
    """
    return LINKEDIN_POST_TEMPLATE.format(custom_closing=custom_closing)
