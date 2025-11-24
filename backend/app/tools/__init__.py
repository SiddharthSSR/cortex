"""Tools package for Cortex."""

from app.tools.base_tool import BaseTool, ToolParameter, ToolResult, ToolDefinition
from app.tools.registry import ToolRegistry, get_tool_registry
from app.tools.calculator import CalculatorTool
from app.tools.web_search import WebSearchTool
from app.tools.python_repl import PythonREPLTool

__all__ = [
    "BaseTool",
    "ToolParameter",
    "ToolResult",
    "ToolDefinition",
    "ToolRegistry",
    "get_tool_registry",
    "CalculatorTool",
    "WebSearchTool",
    "PythonREPLTool",
    "initialize_tools",
]


def initialize_tools(registry: ToolRegistry = None) -> ToolRegistry:
    """Initialize and register all available tools.

    Args:
        registry: Optional registry to use, creates new one if not provided

    Returns:
        ToolRegistry with all tools registered
    """
    if registry is None:
        registry = get_tool_registry()

    # Register all tools
    registry.register(CalculatorTool())
    registry.register(WebSearchTool())
    registry.register(PythonREPLTool())

    return registry
