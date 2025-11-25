"""Chat-related Pydantic schemas."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message role enumeration."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """Chat message schema."""

    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatRequest(BaseModel):
    """Chat completion request schema."""

    messages: List[Message]
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=8192)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    enable_agent: bool = False


class AgentStep(BaseModel):
    """Agent reasoning step."""

    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    status: str = "thinking"


class ChatResponse(BaseModel):
    """Chat completion response schema."""

    id: str
    model: str
    created: int
    message: Message
    usage: Optional[Dict[str, int]] = None
    finish_reason: str = "stop"
    agent_steps: Optional[List[AgentStep]] = None


class StreamChunk(BaseModel):
    """Streaming response chunk schema."""

    id: str
    model: str
    created: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ModelInfo(BaseModel):
    """Model information schema."""

    id: str
    name: str
    type: str = "llm"
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    loaded: bool = False


class ModelsListResponse(BaseModel):
    """Models list response schema."""

    models: List[ModelInfo]
