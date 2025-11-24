"""Tools management endpoints."""

import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.tools import get_tool_registry, initialize_tools

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize tools on module load
initialize_tools()


class ToolInfo(BaseModel):
    """Tool information response."""

    name: str
    description: str
    enabled: bool
    parameters: Dict[str, Any]


class ToolsListResponse(BaseModel):
    """Tools list response."""

    tools: List[ToolInfo]
    total_count: int
    enabled_count: int


class ToolExecutionRequest(BaseModel):
    """Tool execution request."""

    tool_name: str
    parameters: Dict[str, Any]


class ToolExecutionResponse(BaseModel):
    """Tool execution response."""

    success: bool
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


@router.get("/tools", response_model=ToolsListResponse)
async def list_tools(enabled_only: bool = False):
    """List all available tools.

    Args:
        enabled_only: If True, only return enabled tools

    Returns:
        List of available tools
    """
    registry = get_tool_registry()
    tools = registry.list_tools(enabled_only=enabled_only)

    tool_infos = []
    for tool in tools:
        tool_infos.append(
            ToolInfo(
                name=tool.name,
                description=tool.description,
                enabled=tool.enabled,
                parameters={
                    name: {
                        "type": param.type,
                        "description": param.description,
                        "required": param.required,
                        "default": param.default,
                    }
                    for name, param in tool.parameters.items()
                },
            )
        )

    return ToolsListResponse(
        tools=tool_infos,
        total_count=registry.get_tool_count(),
        enabled_count=registry.get_enabled_count(),
    )


@router.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool.

    Args:
        tool_name: Name of the tool

    Returns:
        Tool information
    """
    registry = get_tool_registry()
    tool = registry.get_tool(tool_name)

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    return ToolInfo(
        name=tool.name,
        description=tool.description,
        enabled=tool.enabled,
        parameters={
            name: {
                "type": param.type,
                "description": param.description,
                "required": param.required,
                "default": param.default,
            }
            for name, param in tool.parameters.items()
        },
    )


@router.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """Execute a tool with given parameters.

    Args:
        request: Tool execution request with tool name and parameters

    Returns:
        Tool execution result
    """
    registry = get_tool_registry()

    try:
        result = await registry.execute_tool(request.tool_name, request.parameters)

        return ToolExecutionResponse(
            success=result.success,
            result=result.result,
            error=result.error,
            metadata=result.metadata,
        )

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Tool execution failed: {str(e)}"
        )


@router.post("/tools/{tool_name}/enable")
async def enable_tool(tool_name: str):
    """Enable a tool.

    Args:
        tool_name: Name of the tool to enable

    Returns:
        Success message
    """
    registry = get_tool_registry()
    tool = registry.get_tool(tool_name)

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    registry.enable_tool(tool_name)
    return {"status": "success", "message": f"Tool '{tool_name}' enabled"}


@router.post("/tools/{tool_name}/disable")
async def disable_tool(tool_name: str):
    """Disable a tool.

    Args:
        tool_name: Name of the tool to disable

    Returns:
        Success message
    """
    registry = get_tool_registry()
    tool = registry.get_tool(tool_name)

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    registry.disable_tool(tool_name)
    return {"status": "success", "message": f"Tool '{tool_name}' disabled"}


@router.get("/tools/definitions/openai")
async def get_openai_tool_definitions(enabled_only: bool = True):
    """Get tool definitions in OpenAI function calling format.

    Args:
        enabled_only: If True, only return enabled tools

    Returns:
        List of tool definitions in OpenAI format
    """
    registry = get_tool_registry()
    definitions = registry.get_tool_definitions(enabled_only=enabled_only)

    return {"tools": definitions, "count": len(definitions)}
