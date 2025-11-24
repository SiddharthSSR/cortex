"""Tools package for Cortex."""

from typing import Optional

from app.tools.base_tool import BaseTool, ToolParameter, ToolResult, ToolDefinition
from app.tools.registry import ToolRegistry, get_tool_registry
from app.tools.calculator import CalculatorTool
from app.tools.web_search import WebSearchTool
from app.tools.python_repl import PythonREPLTool
from app.tools.code_generator import CodeGeneratorTool

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
    "CodeGeneratorTool",
    "initialize_tools",
]


def initialize_tools(registry: ToolRegistry = None, llm=None) -> ToolRegistry:
    """Initialize and register all available tools.

    Args:
        registry: Optional registry to use, creates new one if not provided
        llm: Optional LLM instance for tools that require it (e.g., CodeGeneratorTool)

    Returns:
        ToolRegistry with all tools registered
    """
    if registry is None:
        registry = get_tool_registry()

    # Register all tools
    registry.register(CalculatorTool())
    registry.register(WebSearchTool())
    registry.register(PythonREPLTool())

    # Register code generator with LLM if provided
    code_gen = CodeGeneratorTool(llm=llm)
    registry.register(code_gen)

    return registry
