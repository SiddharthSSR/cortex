"""Tool-related Pydantic schemas."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolType(str, Enum):
    """Tool type enumeration."""

    FUNCTION = "function"


class ToolParameter(BaseModel):
    """Tool parameter schema."""

    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None
    items: Optional[Dict[str, Any]] = None


class ToolFunction(BaseModel):
    """Tool function schema."""

    name: str
    description: str
    parameters: Dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}, "required": []}
    )


class Tool(BaseModel):
    """Tool schema."""

    type: ToolType = ToolType.FUNCTION
    function: ToolFunction


class ToolCall(BaseModel):
    """Tool call schema."""

    id: str
    type: ToolType = ToolType.FUNCTION
    function: Dict[str, Any]  # {name: str, arguments: str (JSON)}


class ToolResult(BaseModel):
    """Tool execution result schema."""

    tool_call_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: Optional[float] = None


class ToolExecutionRequest(BaseModel):
    """Tool execution request schema."""

    tool_call: ToolCall
    context: Optional[Dict[str, Any]] = None
