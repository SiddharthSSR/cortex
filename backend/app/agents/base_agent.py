"""Base agent class for all agent implementations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status."""

    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStep(BaseModel):
    """Single step in agent execution."""

    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    status: AgentStatus = AgentStatus.THINKING


class AgentResult(BaseModel):
    """Result from agent execution."""

    success: bool
    final_answer: Optional[str] = None
    steps: List[AgentStep] = Field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentMemory:
    """Memory system for agents."""

    def __init__(self, max_steps: int = 10):
        """Initialize agent memory.

        Args:
            max_steps: Maximum number of steps to remember
        """
        self.max_steps = max_steps
        self.steps: List[AgentStep] = []
        self.context: Dict[str, Any] = {}

    def add_step(self, step: AgentStep):
        """Add a step to memory.

        Args:
            step: Agent step to add
        """
        self.steps.append(step)
        # Keep only last max_steps
        if len(self.steps) > self.max_steps:
            self.steps = self.steps[-self.max_steps :]

    def get_recent_steps(self, n: int = 5) -> List[AgentStep]:
        """Get recent steps.

        Args:
            n: Number of recent steps to retrieve

        Returns:
            List of recent steps
        """
        return self.steps[-n:] if self.steps else []

    def get_all_steps(self) -> List[AgentStep]:
        """Get all steps in memory."""
        return self.steps

    def clear(self):
        """Clear all memory."""
        self.steps = []
        self.context = {}

    def set_context(self, key: str, value: Any):
        """Set a context value.

        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value.

        Args:
            key: Context key
            default: Default value if key not found

        Returns:
            Context value or default
        """
        return self.context.get(key, default)

    def format_history(self) -> str:
        """Format memory as a string for LLM context.

        Returns:
            Formatted history string
        """
        if not self.steps:
            return "No previous steps."

        history = []
        for step in self.steps:
            history.append(f"Step {step.step_number}:")
            history.append(f"  Thought: {step.thought}")
            if step.action:
                history.append(f"  Action: {step.action}")
                if step.action_input:
                    history.append(f"  Input: {step.action_input}")
            if step.observation:
                history.append(f"  Observation: {step.observation}")

        return "\n".join(history)


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        name: str,
        description: str,
        max_iterations: int = 10,
        verbose: bool = False,
    ):
        """Initialize base agent.

        Args:
            name: Agent name
            description: Agent description
            max_iterations: Maximum number of iterations
            verbose: Enable verbose logging
        """
        self.name = name
        self.description = description
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.memory = AgentMemory(max_steps=max_iterations)
        self._current_step = 0
        self._status = AgentStatus.IDLE

    @property
    def status(self) -> AgentStatus:
        """Get current agent status."""
        return self._status

    @abstractmethod
    async def plan(self, goal: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Plan how to achieve the goal.

        Args:
            goal: The goal to achieve
            context: Additional context

        Returns:
            Planning thoughts/strategy
        """
        pass

    @abstractmethod
    async def execute(
        self, goal: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Execute the agent to achieve a goal.

        Args:
            goal: The goal to achieve
            context: Additional context

        Returns:
            AgentResult with execution results
        """
        pass

    def reset(self):
        """Reset agent state."""
        self.memory.clear()
        self._current_step = 0
        self._status = AgentStatus.IDLE
        if self.verbose:
            logger.info(f"Agent '{self.name}' reset")

    def _log(self, message: str):
        """Log message if verbose is enabled.

        Args:
            message: Message to log
        """
        if self.verbose:
            logger.info(f"[{self.name}] {message}")

    def get_capabilities(self) -> List[str]:
        """Get agent capabilities.

        Returns:
            List of capability descriptions
        """
        return []

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary.

        Returns:
            Dictionary representation of agent
        """
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "max_iterations": self.max_iterations,
            "current_step": self._current_step,
            "capabilities": self.get_capabilities(),
        }
