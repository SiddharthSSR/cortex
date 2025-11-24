"""Base model interface for extensibility."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from app.schemas.chat import Message


class BaseModel(ABC):
    """Abstract base class for all model types (LLM, Vision, Audio, Multimodal)."""

    def __init__(self, model_id: str, **kwargs):
        """Initialize the base model.

        Args:
            model_id: Unique identifier for the model
            **kwargs: Additional model-specific configuration
        """
        self.model_id = model_id
        self.config = kwargs
        self._loaded = False

    @abstractmethod
    async def load(self) -> None:
        """Load the model into memory."""
        pass

    @abstractmethod
    async def unload(self) -> None:
        """Unload the model from memory."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Message:
        """Generate a response synchronously.

        Args:
            messages: List of conversation messages
            tools: Optional list of available tools
            **kwargs: Additional generation parameters

        Returns:
            Generated message
        """
        pass

    @abstractmethod
    async def stream_generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Generate a response with streaming.

        Args:
            messages: List of conversation messages
            tools: Optional list of available tools
            **kwargs: Additional generation parameters

        Yields:
            Streaming chunks with delta content
        """
        pass

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded

    @property
    def model_type(self) -> str:
        """Return the type of model (llm, vision, audio, multimodal)."""
        return "base"

    def get_capabilities(self) -> List[str]:
        """Return list of model capabilities."""
        return []
