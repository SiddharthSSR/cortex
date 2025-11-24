"""Tool registry for managing available tools."""

import logging
from typing import Dict, List, Optional, Any
import json

from app.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """Register a tool.

        Args:
            tool: Tool instance to register
        """
        tool_name = tool.name
        if tool_name in self._tools:
            logger.warning(f"Tool '{tool_name}' is already registered. Overwriting.")

        self._tools[tool_name] = tool
        logger.info(f"Registered tool: {tool_name}")

    def unregister(self, tool_name: str):
        """Unregister a tool.

        Args:
            tool_name: Name of the tool to unregister
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
        else:
            logger.warning(f"Tool '{tool_name}' not found in registry")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(tool_name)

    def list_tools(self, enabled_only: bool = False) -> List[BaseTool]:
        """List all registered tools.

        Args:
            enabled_only: If True, only return enabled tools

        Returns:
            List of tool instances
        """
        if enabled_only:
            return [tool for tool in self._tools.values() if tool.enabled]
        return list(self._tools.values())

    def get_tool_definitions(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """Get tool definitions for LLM function calling.

        Args:
            enabled_only: If True, only return enabled tools

        Returns:
            List of tool definitions in OpenAI function calling format
        """
        tools = self.list_tools(enabled_only=enabled_only)
        return [tool.to_dict() for tool in tools]

    async def execute_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> ToolResult:
        """Execute a tool with given parameters.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters

        Returns:
            ToolResult with execution result or error
        """
        tool = self.get_tool(tool_name)

        if tool is None:
            return ToolResult(
                success=False, error=f"Tool '{tool_name}' not found in registry"
            )

        if not tool.enabled:
            return ToolResult(
                success=False, error=f"Tool '{tool_name}' is currently disabled"
            )

        logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")

        try:
            result = await tool.safe_execute(**parameters)
            logger.info(
                f"Tool '{tool_name}' executed successfully: {result.success}"
            )
            return result
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {e}")
            return ToolResult(
                success=False, error=f"Unexpected error executing tool: {str(e)}"
            )

    async def execute_tool_call(self, tool_call: Dict[str, Any]) -> ToolResult:
        """Execute a tool call from LLM function calling format.

        Args:
            tool_call: Tool call in OpenAI format with 'function' key

        Returns:
            ToolResult with execution result or error
        """
        try:
            function = tool_call.get("function", {})
            tool_name = function.get("name")
            arguments_str = function.get("arguments", "{}")

            if not tool_name:
                return ToolResult(success=False, error="Tool name not provided")

            # Parse arguments from JSON string
            try:
                parameters = json.loads(arguments_str)
            except json.JSONDecodeError as e:
                return ToolResult(
                    success=False, error=f"Invalid JSON arguments: {str(e)}"
                )

            return await self.execute_tool(tool_name, parameters)

        except Exception as e:
            return ToolResult(
                success=False, error=f"Failed to parse tool call: {str(e)}"
            )

    def enable_tool(self, tool_name: str):
        """Enable a tool.

        Args:
            tool_name: Name of the tool to enable
        """
        tool = self.get_tool(tool_name)
        if tool:
            tool.enable()
            logger.info(f"Enabled tool: {tool_name}")
        else:
            logger.warning(f"Tool '{tool_name}' not found")

    def disable_tool(self, tool_name: str):
        """Disable a tool.

        Args:
            tool_name: Name of the tool to disable
        """
        tool = self.get_tool(tool_name)
        if tool:
            tool.disable()
            logger.info(f"Disabled tool: {tool_name}")
        else:
            logger.warning(f"Tool '{tool_name}' not found")

    def get_tool_count(self) -> int:
        """Get count of registered tools."""
        return len(self._tools)

    def get_enabled_count(self) -> int:
        """Get count of enabled tools."""
        return len([t for t in self._tools.values() if t.enabled])


# Global tool registry instance
_global_registry = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
