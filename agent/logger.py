"""
Logging utilities for agent execution traces
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from agent.memory import AgentState
from rag.config import LOG_DIR, LOG_LEVEL


class AgentLogger:
    """Logger for agent execution traces"""

    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir or LOG_DIR)
        self.log_dir.mkdir(exist_ok=True, parents=True)

        # Setup file logging
        self.trace_log = self.log_dir / "agent_traces.log"
        self.tool_log = self.log_dir / "tool_calls.log"

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("AgentOrchestrator")

    def log_query(self, query: str) -> None:
        """Log incoming query"""
        self.logger.info(f"New query: {query}")

    def log_state(self, state: AgentState) -> None:
        """Log agent state"""
        trace_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": state.query,
            "iteration": state.iteration,
            "confidence": state.confidence_score,
            "is_complete": state.is_complete,
            "steps": len(state.reasoning_steps)
        }

        with open(self.trace_log, 'a') as f:
            f.write(json.dumps(trace_entry) + "\n")

    def log_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Any,
        success: bool
    ) -> None:
        """Log tool execution"""
        tool_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "params": params,
            "success": success,
            "result": str(result)[:200]  # Truncate
        }

        with open(self.tool_log, 'a') as f:
            f.write(json.dumps(tool_entry) + "\n")

    def save_detailed_trace(self, state: AgentState) -> str:
        """Save detailed execution trace"""
        filename = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.log_dir / filename

        trace_data = state.to_dict()
        trace_data["timestamp"] = datetime.now().isoformat()
        trace_data["final_answer"] = state.current_answer

        with open(filepath, 'w') as f:
            json.dump(trace_data, f, indent=2)

        return str(filepath)
