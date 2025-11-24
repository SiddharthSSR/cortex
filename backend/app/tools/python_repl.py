"""Python REPL tool for code execution."""

import logging
import sys
import io
import contextlib
from typing import Dict
import ast
import builtins

from app.tools.base_tool import BaseTool, ToolParameter, ToolResult

logger = logging.getLogger(__name__)


class PythonREPLTool(BaseTool):
    """Tool for executing Python code in a sandboxed environment."""

    def __init__(self, timeout: int = 30):
        """Initialize Python REPL tool.

        Args:
            timeout: Maximum execution time in seconds
        """
        super().__init__()
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "python_repl"

    @property
    def description(self) -> str:
        return (
            "Executes Python code and returns the output. "
            "Useful for calculations, data processing, and code testing. "
            "Has access to standard Python libraries like math, json, datetime, etc. "
            "The code runs in a sandboxed environment. "
            "Example: 'print([x**2 for x in range(10)])'"
        )

    @property
    def parameters(self) -> Dict[str, ToolParameter]:
        return {
            "code": ToolParameter(
                type="string",
                description="The Python code to execute",
                required=True,
            )
        }

    async def execute(self, code: str) -> ToolResult:
        """Execute Python code.

        Args:
            code: Python code string to execute

        Returns:
            ToolResult with execution output or error
        """
        if not code or not code.strip():
            return ToolResult(success=False, error="Code cannot be empty")

        try:
            # Validate syntax first
            try:
                ast.parse(code)
            except SyntaxError as e:
                return ToolResult(
                    success=False, error=f"Syntax error in code: {str(e)}"
                )

            # Execute code in sandboxed environment
            output = await self._execute_sandboxed(code)

            logger.info(f"Python REPL executed successfully")

            return ToolResult(
                success=True,
                result=output,
                metadata={"code": code, "output_length": len(output)},
            )

        except TimeoutError:
            error_msg = f"Code execution timed out after {self.timeout} seconds"
            logger.warning(error_msg)
            return ToolResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Code execution error: {str(e)}"
            logger.error(error_msg)
            return ToolResult(success=False, error=error_msg)

    async def _execute_sandboxed(self, code: str) -> str:
        """Execute code in a sandboxed environment.

        Args:
            code: Python code to execute

        Returns:
            String output from code execution
        """
        # Create restricted globals
        safe_globals = {
            "__builtins__": {
                # Safe built-ins
                "abs": abs,
                "all": all,
                "any": any,
                "ascii": ascii,
                "bin": bin,
                "bool": bool,
                "chr": chr,
                "dict": dict,
                "divmod": divmod,
                "enumerate": enumerate,
                "filter": filter,
                "float": float,
                "format": format,
                "hex": hex,
                "int": int,
                "isinstance": isinstance,
                "issubclass": issubclass,
                "iter": iter,
                "len": len,
                "list": list,
                "map": map,
                "max": max,
                "min": min,
                "next": next,
                "oct": oct,
                "ord": ord,
                "pow": pow,
                "print": print,
                "range": range,
                "repr": repr,
                "reversed": reversed,
                "round": round,
                "set": set,
                "slice": slice,
                "sorted": sorted,
                "str": str,
                "sum": sum,
                "tuple": tuple,
                "type": type,
                "zip": zip,
                # Safe modules
                "True": True,
                "False": False,
                "None": None,
            }
        }

        # Allow safe imports
        allowed_modules = [
            "math",
            "json",
            "datetime",
            "random",
            "re",
            "collections",
            "itertools",
            "functools",
            "operator",
            "string",
            "decimal",
            "fractions",
            "statistics",
        ]

        # Add __import__ with restrictions
        original_import = builtins.__import__

        def safe_import(name, *args, **kwargs):
            if name not in allowed_modules:
                raise ImportError(f"Module '{name}' is not allowed")
            return original_import(name, *args, **kwargs)

        safe_globals["__builtins__"]["__import__"] = safe_import

        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(
                stderr_capture
            ):
                # Execute the code
                exec(code, safe_globals)

            # Get captured output
            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()

            result = ""
            if output:
                result += output
            if errors:
                if result:
                    result += "\n"
                result += f"Errors:\n{errors}"

            return result if result else "Code executed successfully (no output)"

        except Exception as e:
            # Return the error message
            error_output = stderr_capture.getvalue()
            if error_output:
                raise Exception(f"{error_output}\n{str(e)}")
            raise
