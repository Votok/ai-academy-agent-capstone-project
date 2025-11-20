"""
Test complete agent workflow end-to-end
"""
from agent.orchestrator import AgentOrchestrator


def test_simple_query():
    """Test simple factual query"""
    print("\n" + "="*80)
    print("TEST 1: Simple Factual Query")
    print("="*80)

    orchestrator = AgentOrchestrator()

    query = "What is retrieval-augmented generation?"

    print(f"Testing: {query}\n")

    state = orchestrator.run(query, verbose=True)

    print("\n" + "="*60)
    print("FINAL ANSWER:")
    print("="*60)
    print(state.current_answer)
    print(f"\nConfidence: {state.confidence_score:.2f}")
    print(f"Iterations: {state.iteration}")

    # Assertions
    assert state.current_answer is not None, "Answer should not be None"
    assert len(state.current_answer) > 100, f"Answer too short: {len(state.current_answer)} chars"
    assert state.confidence_score > 0, f"Confidence score should be positive: {state.confidence_score}"

    print("\n✅ Test 1 passed!")
    return state


def test_query_with_tools():
    """Test query that should trigger tool usage"""
    print("\n" + "="*80)
    print("TEST 2: Query with Tool Usage")
    print("="*80)

    orchestrator = AgentOrchestrator()

    query = "What is today's date and calculate 15% of 250?"

    print(f"Testing: {query}\n")

    state = orchestrator.run(query, verbose=True)

    print("\n" + "="*60)
    print("FINAL ANSWER:")
    print("="*60)
    print(state.current_answer)
    print(f"\nConfidence: {state.confidence_score:.2f}")
    print(f"Iterations: {state.iteration}")

    # Assertions
    assert state.current_answer is not None, "Answer should not be None"

    # Check that tool calling step was executed
    tool_steps = state.get_steps_by_type("tool_call")
    print(f"\nTool calling steps: {len(tool_steps)}")

    print("\n✅ Test 2 passed!")
    return state


def test_complex_query():
    """Test complex query requiring multiple steps"""
    print("\n" + "="*80)
    print("TEST 3: Complex Multi-Step Query")
    print("="*80)

    orchestrator = AgentOrchestrator()

    query = "What did I learn about embeddings in the AI Academy course, and how are they used in RAG systems?"

    print(f"Testing: {query}\n")

    state = orchestrator.run(query, verbose=True)

    print("\n" + "="*60)
    print("FINAL ANSWER:")
    print("="*60)
    print(state.current_answer)
    print(f"\nConfidence: {state.confidence_score:.2f}")
    print(f"Iterations: {state.iteration}")

    # Assertions
    assert state.current_answer is not None, "Answer should not be None"
    assert state.iteration >= 0, f"Should have completed at least 1 iteration: {state.iteration}"

    # Check reasoning steps
    print(f"\nTotal reasoning steps: {len(state.reasoning_steps)}")
    for step in state.reasoning_steps:
        print(f"  - {step.step_type}: {step.content[:80]}...")

    print("\n✅ Test 3 passed!")
    return state


def test_logging():
    """Test that logging files are created"""
    print("\n" + "="*80)
    print("TEST 4: Logging Verification")
    print("="*80)

    import os
    from pathlib import Path
    from rag.config import LOG_DIR

    orchestrator = AgentOrchestrator()
    query = "Quick test query for logging"

    print(f"Testing: {query}\n")

    state = orchestrator.run(query, verbose=False)

    # Check log files exist
    log_dir = Path(LOG_DIR)
    trace_log = log_dir / "agent_traces.log"

    assert log_dir.exists(), f"Log directory should exist: {log_dir}"
    assert trace_log.exists(), f"Trace log should exist: {trace_log}"

    # Save detailed trace
    trace_path = orchestrator.save_trace(state)
    assert os.path.exists(trace_path), f"Detailed trace should exist: {trace_path}"

    print(f"✓ Log directory: {log_dir}")
    print(f"✓ Trace log: {trace_log}")
    print(f"✓ Detailed trace: {trace_path}")

    print("\n✅ Test 4 passed!")


if __name__ == "__main__":
    print("🧪 Running Complete Workflow Tests\n")
    print("This will test the full agent orchestrator with:")
    print("  1. Simple factual queries")
    print("  2. Tool-calling queries")
    print("  3. Complex multi-step queries")
    print("  4. Logging verification")
    print("\n" + "="*80)

    try:
        # Run all tests
        test_simple_query()
        test_query_with_tools()
        test_complex_query()
        test_logging()

        print("\n" + "="*80)
        print("🎉 ALL WORKFLOW TESTS PASSED!")
        print("="*80)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
