"""
Main agent orchestrator
Coordinates all agent capabilities into unified workflow
"""
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from agent.memory import AgentState, ReasoningStep
from agent.reasoning import ReasoningPlanner
from agent.reflection import SelfReflectionCritic
from agent.prompts import AGENT_SYSTEM_PROMPT, format_answer_prompt, format_revision_prompt
from agent.logger import AgentLogger
from rag.retriever import retrieve_relevant_chunks
from rag.config import (
    OPENAI_API_KEY,
    AGENT_MODEL,
    AGENT_TEMPERATURE,
    MAX_REASONING_STEPS,
    TOP_K,
    REFLECTION_ENABLED
)
from tools import get_global_registry
from tools.base import ToolResult

from openai import OpenAI


class AgentOrchestrator:
    """
    Main agent orchestrator
    Coordinates reasoning, RAG, tools, and reflection
    """

    def __init__(self):
        self.planner = ReasoningPlanner()
        self.critic = SelfReflectionCritic()
        self.tool_registry = get_global_registry()
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.logger = AgentLogger()

    def run(
        self,
        query: str,
        verbose: bool = False,
        max_iterations: Optional[int] = None
    ) -> AgentState:
        """
        Execute complete agent workflow

        Args:
            query: User query
            verbose: Print detailed execution trace
            max_iterations: Override default max iterations

        Returns:
            AgentState with full execution history
        """
        # Initialize state
        max_iter = max_iterations or MAX_REASONING_STEPS
        state = AgentState(query=query, max_iterations=max_iter)

        self.logger.log_query(query)

        if verbose:
            print(f"\n{'='*60}")
            print(f"🚀 Agent Workflow Started")
            print(f"Query: {query}")
            print(f"{'='*60}\n")

        # === Phase 1: PLANNING ===
        if verbose:
            print("🧠 Phase 1: Planning")

        plan = self._plan(query, state, verbose)

        # Determine collections to search
        collections = self.planner.identify_collections(query)
        if verbose:
            print(f"   📚 Target collections: {', '.join(collections)}")

        # Check if tools are needed
        needs_tools = self.planner.should_use_tools(query)
        if verbose:
            print(f"   🔧 Tools needed: {needs_tools}")

        # === Iterative Workflow Loop ===
        while state.should_continue():
            iteration_num = state.iteration + 1
            if verbose:
                print(f"\n🔄 Iteration {iteration_num}/{state.max_iterations}")

            # === Phase 2: RETRIEVAL ===
            if verbose:
                print("   🔍 Phase 2: Retrieval")

            context_docs = self._retrieve(query, collections, state, verbose)

            # === Phase 3: TOOL CALLING ===
            tool_results = []
            if needs_tools:
                if verbose:
                    print("   🔧 Phase 3: Tool Calling")
                tool_results = self._call_tools(query, context_docs, state, verbose)

            # === Phase 4: GENERATION ===
            if verbose:
                print("   ✍️  Phase 4: Generation")

            answer = self._generate(
                query, context_docs, tool_results, state, verbose
            )

            state.current_answer = answer

            # === Phase 5: REFLECTION ===
            if REFLECTION_ENABLED:
                if verbose:
                    print("   🤔 Phase 5: Reflection")

                reflection = self._reflect(query, answer, context_docs, state, verbose)

                # === Phase 6: REVISE? ===
                should_revise = self.critic.should_revise(reflection)

                if should_revise and state.should_continue():
                    if verbose:
                        print("   🔄 Phase 6: Revision needed, continuing...")

                    # Prepare feedback for next iteration
                    feedback = self._format_reflection_feedback(reflection)
                    state.reflection_feedback.append(feedback)

                    state.increment_iteration()
                    continue  # Next iteration
                else:
                    if verbose:
                        print("   ✅ Answer is satisfactory")
                    state.is_complete = True
                    break
            else:
                # No reflection, accept answer
                state.is_complete = True
                break

        # === Phase 7: FINALIZATION ===
        if verbose:
            print(f"\n{'='*60}")
            print(f"🎯 Workflow Complete")
            print(f"Iterations: {state.iteration}")
            print(f"Confidence: {state.confidence_score:.2f}")
            print(f"{'='*60}\n")

        # Log final state
        self.logger.log_state(state)

        return state

    def _plan(
        self,
        query: str,
        state: AgentState,
        verbose: bool
    ) -> Any:
        """Planning phase"""
        plan = self.planner.plan(query)

        state.add_step("plan", f"Main goal: {plan.main_goal}", {
            "sub_tasks": plan.sub_tasks,
            "complexity": plan.complexity,
            "required_information": plan.required_information
        })

        if verbose:
            print(f"   Goal: {plan.main_goal}")
            print(f"   Complexity: {plan.complexity}")
            print(f"   Sub-tasks: {len(plan.sub_tasks)}")

        return plan

    def _retrieve(
        self,
        query: str,
        collections: List[str],
        state: AgentState,
        verbose: bool
    ) -> List[Any]:
        """Retrieval phase"""
        all_docs = []

        for collection in collections:
            try:
                results = retrieve_relevant_chunks(
                    query=query,
                    collection_name=collection,
                    top_k=3
                )
                all_docs.extend(results)

                if verbose:
                    print(f"      {collection}: {len(results)} documents")

            except Exception as e:
                if verbose:
                    print(f"      {collection}: Error - {e}")

        # Limit total docs
        all_docs = all_docs[:TOP_K]

        state.add_step("retrieve", f"Retrieved {len(all_docs)} documents", {
            "collections": collections,
            "doc_count": len(all_docs)
        })

        return all_docs

    def _call_tools(
        self,
        query: str,
        context_docs: List[Any],
        state: AgentState,
        verbose: bool
    ) -> List[Dict[str, Any]]:
        """Tool calling phase using OpenAI function calling"""
        tool_results = []

        # Get available tool schemas
        tool_schemas = self.tool_registry.get_tool_schemas()

        if not tool_schemas:
            return tool_results

        # Prepare context for tool selection
        context_preview = "\n".join([
            doc.page_content[:200] for doc in context_docs[:2]
        ]) if context_docs else ""

        tool_selection_prompt = f"""Query: {query}

Context preview:
{context_preview}

Based on this query, determine which tools (if any) should be called and with what parameters.
Consider:
- Does the query require calculations?
- Does it need current date/time information?
- Does it need formatting (table, list)?
- Does it need additional database searches?
"""

        try:
            # Use OpenAI function calling to select tools
            response = self.client.chat.completions.create(
                model=AGENT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant with access to tools. Decide which tools to call based on the user's query."},
                    {"role": "user", "content": tool_selection_prompt}
                ],
                tools=tool_schemas,
                tool_choice="auto",
                temperature=0.3
            )

            # Check if tools were called
            message = response.choices[0].message

            if message.tool_calls:
                if verbose:
                    print(f"      Selected {len(message.tool_calls)} tools")

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    if verbose:
                        print(f"      Calling {tool_name}...")

                    # Execute tool
                    result = self.tool_registry.execute(tool_name, **tool_args)

                    # Log tool call
                    self.logger.log_tool_call(
                        tool_name=tool_name,
                        params=tool_args,
                        result=result.result,
                        success=result.success
                    )

                    tool_results.append({
                        "tool": tool_name,
                        "success": result.success,
                        "result": result.result,
                        "error": result.error
                    })

                    if verbose:
                        if result.success:
                            result_str = str(result.result)
                            print(f"         ✓ Success: {result_str[:100]}")
                        else:
                            print(f"         ✗ Error: {result.error}")
            else:
                if verbose:
                    print("      No tools needed for this query")

        except Exception as e:
            if verbose:
                print(f"      Tool calling error: {e}")

        state.add_step("tool_call", f"Called {len(tool_results)} tools", {
            "tools": [t["tool"] for t in tool_results]
        })

        return tool_results

    def _generate(
        self,
        query: str,
        context_docs: List[Any],
        tool_results: List[Dict[str, Any]],
        state: AgentState,
        verbose: bool
    ) -> str:
        """Generation phase"""

        # Prepare context
        context_texts = [doc.page_content for doc in context_docs]

        # Add tool results to context
        if tool_results:
            tool_context = self._format_tool_results(tool_results)
            context_texts.append(f"\n\nTool Results:\n{tool_context}")

        # Choose prompt based on iteration
        if state.reflection_feedback:
            # Revision prompt
            prompt = format_revision_prompt(
                query=query,
                previous_answer=state.current_answer or "",
                feedback=state.reflection_feedback[-1],
                context=context_texts
            )
        else:
            # Initial prompt
            prompt = format_answer_prompt(query=query, context=context_texts)

        # Generate answer
        response = self.client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=AGENT_TEMPERATURE
        )

        answer = response.choices[0].message.content

        state.add_step("generate", answer[:200] + "...", {
            "context_count": len(context_docs),
            "tool_results_count": len(tool_results)
        })

        if verbose:
            print(f"      Generated {len(answer)} characters")

        return answer

    def _reflect(
        self,
        query: str,
        answer: str,
        context_docs: List[Any],
        state: AgentState,
        verbose: bool
    ) -> Any:
        """Reflection phase"""
        context_texts = [doc.page_content[:300] for doc in context_docs[:3]]

        reflection = self.critic.reflect(query, answer, context_texts)

        state.confidence_score = reflection.confidence_score

        state.add_step("reflect", f"Confidence: {reflection.confidence_score:.2f}", {
            "satisfactory": reflection.is_satisfactory,
            "strengths": reflection.strengths,
            "weaknesses": reflection.weaknesses,
            "suggestions": reflection.suggestions
        })

        if verbose:
            print(f"      Confidence: {reflection.confidence_score:.2f}")
            print(f"      Satisfactory: {reflection.is_satisfactory}")
            if reflection.weaknesses:
                print(f"      Weaknesses: {', '.join(reflection.weaknesses[:2])}")

        return reflection

    def _format_reflection_feedback(self, reflection: Any) -> str:
        """Format reflection into feedback string"""
        feedback_parts = []

        if reflection.weaknesses:
            feedback_parts.append("Weaknesses:")
            for w in reflection.weaknesses:
                feedback_parts.append(f"  - {w}")

        if reflection.suggestions:
            feedback_parts.append("\nSuggestions:")
            for s in reflection.suggestions:
                feedback_parts.append(f"  - {s}")

        if reflection.missing_information:
            feedback_parts.append("\nMissing Information:")
            for m in reflection.missing_information:
                feedback_parts.append(f"  - {m}")

        return "\n".join(feedback_parts)

    def _format_tool_results(self, tool_results: List[Dict[str, Any]]) -> str:
        """Format tool results for context"""
        formatted = []
        for tr in tool_results:
            if tr["success"]:
                formatted.append(f"- {tr['tool']}: {tr['result']}")
            else:
                formatted.append(f"- {tr['tool']}: Error - {tr['error']}")
        return "\n".join(formatted)

    def save_trace(self, state: AgentState, output_path: str = None) -> str:
        """Save execution trace to file"""
        if output_path:
            trace = state.to_dict()
            trace["timestamp"] = datetime.now().isoformat()
            trace["final_answer"] = state.current_answer

            with open(output_path, 'w') as f:
                json.dump(trace, f, indent=2)

            print(f"✓ Trace saved to {output_path}")
            return output_path
        else:
            return self.logger.save_detailed_trace(state)


# CLI for testing
if __name__ == "__main__":
    orchestrator = AgentOrchestrator()

    test_query = "What is RAG and why is it useful?"

    print(f"Testing agent orchestrator...")
    print(f"Query: {test_query}\n")

    state = orchestrator.run(test_query, verbose=True)

    print("\n" + "="*60)
    print("🎯 FINAL ANSWER:")
    print("="*60)
    print(state.current_answer)
    print(f"\n📊 Confidence: {state.confidence_score:.2f}")
    print(f"🔄 Iterations: {state.iteration}")

    # Save trace
    trace_path = orchestrator.save_trace(state)
    print(f"\n💾 Trace saved: {trace_path}")
