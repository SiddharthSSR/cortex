"""Base tool class for all tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Tool parameter definition."""

    type: str
    description: str
    required: bool = True
    enum: Optional[list] = None
    default: Optional[Any] = None


class ToolDefinition(BaseModel):
    """Tool definition schema for LLM function calling."""

    name: str
    description: str
    parameters: Dict[str, ToolParameter] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []

        for param_name, param in self.parameters.items():
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default

            properties[param_name] = prop

            if param.required:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


class ToolResult(BaseModel):
    """Result from tool execution."""

    success: bool
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(self):
        """Initialize the tool."""
        self._enabled = True

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, ToolParameter]:
        """Tool parameters definition."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with success status and result/error
        """
        pass

    @property
    def enabled(self) -> bool:
        """Check if tool is enabled."""
        return self._enabled

    def enable(self):
        """Enable the tool."""
        self._enabled = True

    def disable(self):
        """Disable the tool."""
        self._enabled = False

    def get_definition(self) -> ToolDefinition:
        """Get tool definition for LLM function calling."""
        return ToolDefinition(
            name=self.name, description=self.description, parameters=self.parameters
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format."""
        return self.get_definition().to_dict()

    async def safe_execute(self, **kwargs) -> ToolResult:
        """Execute tool with error handling.

        Args:
            **kwargs: Tool parameters

        Returns:
            ToolResult with execution result or error
        """
        if not self.enabled:
            return ToolResult(
                success=False, error=f"Tool '{self.name}' is currently disabled"
            )

        try:
            return await self.execute(**kwargs)
        except Exception as e:
            return ToolResult(
                success=False, error=f"Tool execution failed: {str(e)}"
            )
