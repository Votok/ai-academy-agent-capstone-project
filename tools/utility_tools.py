"""
Utility tools for calculations, dates, and other common operations
"""
import math
from datetime import datetime
from typing import List

from tools.base import BaseTool, ToolResult, ToolParameter, ToolCategory


class CalculatorTool(BaseTool):
    """Perform mathematical calculations"""

    def __init__(self):
        super().__init__()
        self.category = ToolCategory.CALCULATION

    def get_description(self) -> str:
        return "Evaluate mathematical expressions (e.g., '2 + 2', '15% of 250')"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                type="string",
                description="Mathematical expression to evaluate",
                required=True
            )
        ]

    def execute(self, expression: str) -> ToolResult:
        """Evaluate math expression safely"""
        try:
            # Handle percentage expressions
            if "%" in expression:
                expression = expression.replace("%", "/100")

            # Handle "of" keyword (e.g., "15% of 250")
            if " of " in expression:
                parts = expression.split(" of ")
                if len(parts) == 2:
                    expression = f"({parts[0]}) * ({parts[1]})"

            # Safe eval with limited builtins
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow,
                "sqrt": math.sqrt, "pi": math.pi, "e": math.e
            }

            result = eval(expression, {"__builtins__": {}}, allowed_names)

            return ToolResult(
                success=True,
                result=result
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Calculation error: {str(e)}"
            )


class GetCurrentDateTool(BaseTool):
    """Get current date and time"""

    def __init__(self):
        super().__init__()
        self.category = ToolCategory.UTILITY

    def get_description(self) -> str:
        return "Get the current date and time"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="format",
                type="string",
                description="Date format (date, time, datetime, or custom strftime)",
                required=False,
                default="datetime"
            )
        ]

    def execute(self, format: str = "datetime") -> ToolResult:
        """Get current date/time"""
        try:
            now = datetime.now()

            if format == "date":
                result = now.strftime("%Y-%m-%d")
            elif format == "time":
                result = now.strftime("%H:%M:%S")
            elif format == "datetime":
                result = now.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Custom strftime format
                result = now.strftime(format)

            return ToolResult(success=True, result=result)

        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))
