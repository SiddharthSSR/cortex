"""Calculator tool for mathematical computations."""

import logging
from typing import Dict

from sympy import sympify, SympifyError
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)

from app.tools.base_tool import BaseTool, ToolParameter, ToolResult

logger = logging.getLogger(__name__)


class CalculatorTool(BaseTool):
    """Tool for evaluating mathematical expressions."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Evaluates mathematical expressions and returns the result. "
            "Supports basic arithmetic (+, -, *, /), exponents (**), "
            "trigonometric functions (sin, cos, tan), logarithms (log, ln), "
            "square roots (sqrt), and constants (pi, e). "
            "Examples: '2 + 2', 'sqrt(16)', 'sin(pi/2)', '2**8'"
        )

    @property
    def parameters(self) -> Dict[str, ToolParameter]:
        return {
            "expression": ToolParameter(
                type="string",
                description="The mathematical expression to evaluate",
                required=True,
            )
        }

    async def execute(self, expression: str) -> ToolResult:
        """Execute the calculator tool.

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            ToolResult with the calculated result or error
        """
        if not expression or not expression.strip():
            return ToolResult(success=False, error="Expression cannot be empty")

        try:
            # Parse and evaluate the expression safely using sympy
            transformations = standard_transformations + (
                implicit_multiplication_application,
            )

            # Parse the expression
            expr = parse_expr(expression, transformations=transformations)

            # Evaluate numerically
            result = expr.evalf()

            # Convert to float if possible, otherwise keep as sympy object
            try:
                result_value = float(result)
                # Check for special float values
                if result_value == float("inf"):
                    result_str = "Infinity"
                elif result_value == float("-inf"):
                    result_str = "-Infinity"
                elif result_value != result_value:  # NaN check
                    result_str = "Undefined (NaN)"
                else:
                    # Format nicely
                    if result_value.is_integer():
                        result_str = str(int(result_value))
                    else:
                        result_str = str(result_value)
            except (TypeError, OverflowError):
                # Complex numbers or other types
                result_str = str(result)

            logger.info(f"Calculator: {expression} = {result_str}")

            return ToolResult(
                success=True,
                result=result_str,
                metadata={
                    "expression": expression,
                    "raw_result": str(result),
                },
            )

        except SympifyError as e:
            error_msg = f"Invalid mathematical expression: {str(e)}"
            logger.warning(f"Calculator error: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except ZeroDivisionError:
            error_msg = "Division by zero"
            logger.warning(f"Calculator error: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Calculation error: {str(e)}"
            logger.error(f"Calculator unexpected error: {error_msg}")
            return ToolResult(success=False, error=error_msg)
