"""
Agent state and memory management
Tracks reasoning history across iterations
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReasoningStep:
    """Single step in reasoning process"""
    step_number: int
    step_type: str  # "plan", "execute", "reflect", "revise"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentState:
    """
    Agent state across reasoning iterations
    Tracks full reasoning trace
    """
    query: str
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    current_answer: Optional[str] = None
    confidence_score: float = 0.0
    iteration: int = 0
    max_iterations: int = 5
    is_complete: bool = False
    reflection_feedback: List[str] = field(default_factory=list)

    def add_step(
        self,
        step_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a reasoning step"""
        step = ReasoningStep(
            step_number=len(self.reasoning_steps) + 1,
            step_type=step_type,
            content=content,
            metadata=metadata or {}
        )
        self.reasoning_steps.append(step)

    def get_steps_by_type(self, step_type: str) -> List[ReasoningStep]:
        """Get all steps of a specific type"""
        return [step for step in self.reasoning_steps if step.step_type == step_type]

    def increment_iteration(self) -> None:
        """Move to next iteration"""
        self.iteration += 1
        if self.iteration >= self.max_iterations:
            self.is_complete = True

    def should_continue(self) -> bool:
        """Check if agent should continue iterating"""
        if self.is_complete:
            return False
        if self.iteration >= self.max_iterations:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "query": self.query,
            "iterations": self.iteration,
            "confidence": self.confidence_score,
            "is_complete": self.is_complete,
            "steps": [
                {
                    "number": step.step_number,
                    "type": step.step_type,
                    "content": step.content[:200] + "..." if len(step.content) > 200 else step.content,
                }
                for step in self.reasoning_steps
            ]
        }
