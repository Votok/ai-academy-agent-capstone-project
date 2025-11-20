"""
Complete reasoning loop integrating planning, execution, reflection, and revision
"""
from typing import Optional, List
from openai import OpenAI

from agent.memory import AgentState
from agent.reasoning import ReasoningPlanner
from agent.reflection import SelfReflectionCritic
from agent.prompts import (
    AGENT_SYSTEM_PROMPT,
    format_answer_prompt,
    format_revision_prompt
)
from rag.retriever import retrieve_relevant_chunks
from rag.config import (
    OPENAI_API_KEY,
    AGENT_MODEL,
    AGENT_TEMPERATURE,
    MAX_REASONING_STEPS,
    TOP_K,
    REFLECTION_ENABLED
)


class ReasoningAgent:
    """
    Agent with full reasoning loop:
    Plan → Execute → Reflect → Revise → Repeat
    """

    def __init__(self):
        self.planner = ReasoningPlanner()
        self.critic = SelfReflectionCritic()
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def run(self, query: str) -> AgentState:
        """
        Execute full reasoning loop for a query
        """
        # Initialize state
        state = AgentState(
            query=query,
            max_iterations=MAX_REASONING_STEPS
        )

        # Phase 1: Planning
        print("🧠 Phase 1: Planning")
        plan = self.planner.plan(query)
        state.add_step("plan", f"Main goal: {plan.main_goal}", {
            "sub_tasks": plan.sub_tasks,
            "complexity": plan.complexity
        })

        # Identify collections to search
        collections = self.planner.identify_collections(query)
        print(f"   📚 Will search collections: {', '.join(collections)}")

        # Reasoning loop
        while state.should_continue():
            print(f"\n🔄 Iteration {state.iteration + 1}/{state.max_iterations}")

            # Phase 2: Execution (Retrieve + Generate)
            print("   🔍 Phase 2: Retrieval")
            context_docs = self._retrieve_context(query, collections)
            context_texts = [doc.page_content for doc in context_docs]

            print("   ✍️  Phase 2: Generation")
            answer = self._generate_answer(query, context_texts, state)
            state.current_answer = answer
            state.add_step("execute", answer, {"context_count": len(context_docs)})

            # Phase 3: Reflection
            if REFLECTION_ENABLED:
                print("   🤔 Phase 3: Reflection")
                reflection = self.critic.reflect(query, answer, context_texts[:3])
                state.confidence_score = reflection.confidence_score

                reflection_summary = f"Confidence: {reflection.confidence_score:.2f}"
                if reflection.weaknesses:
                    reflection_summary += f", Weaknesses: {', '.join(reflection.weaknesses)}"

                state.add_step("reflect", reflection_summary, {
                    "satisfactory": reflection.is_satisfactory,
                    "suggestions": reflection.suggestions
                })

                print(f"      Confidence: {reflection.confidence_score:.2f}")
                print(f"      Satisfactory: {reflection.is_satisfactory}")

                # Phase 4: Decide whether to revise
                if self.critic.should_revise(reflection) and state.should_continue():
                    print("   🔄 Phase 4: Revision needed")
                    state.increment_iteration()

                    # Generate revision prompt with feedback
                    feedback = "\n".join([
                        f"- {w}" for w in reflection.weaknesses
                    ] + [
                        f"Suggestion: {s}" for s in reflection.suggestions
                    ])

                    state.reflection_feedback.append(feedback)

                    # Continue to next iteration with revision
                    continue
                else:
                    print("   ✅ Answer is satisfactory")
                    state.is_complete = True
                    break
            else:
                # No reflection enabled, accept answer
                state.is_complete = True
                break

        return state

    def _retrieve_context(
        self,
        query: str,
        collections: List[str]
    ) -> List:
        """Retrieve relevant context from specified collections"""
        all_results = []

        for collection in collections:
            try:
                results = retrieve_relevant_chunks(
                    query=query,
                    collection_name=collection,
                    top_k=3
                )
                all_results.extend(results)
            except Exception as e:
                # Skip collection if it doesn't exist or has errors
                print(f"      Warning: Could not retrieve from {collection}: {e}")
                continue

        return all_results[:TOP_K]

    def _generate_answer(
        self,
        query: str,
        context: List[str],
        state: AgentState
    ) -> str:
        """Generate answer using LLM"""

        # Use revision prompt if we have feedback
        if state.reflection_feedback:
            prompt = format_revision_prompt(
                query=query,
                previous_answer=state.current_answer or "",
                feedback=state.reflection_feedback[-1],
                context=context
            )
        else:
            prompt = format_answer_prompt(query=query, context=context)

        response = self.client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=AGENT_TEMPERATURE
        )

        return response.choices[0].message.content


# CLI for testing
if __name__ == "__main__":
    agent = ReasoningAgent()

    test_query = "What is retrieval-augmented generation and why is it useful?"

    print(f"Query: {test_query}\n")
    print("="*60)

    state = agent.run(test_query)

    print("\n" + "="*60)
    print("🎯 Final Answer:")
    print(state.current_answer)
    print(f"\n📊 Confidence: {state.confidence_score:.2f}")
    print(f"🔄 Iterations: {state.iteration}")
