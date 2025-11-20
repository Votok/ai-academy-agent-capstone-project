"""
Tools for formatting outputs (tables, lists, markdown)
"""
from typing import List, Dict, Any
from tools.base import BaseTool, ToolResult, ToolParameter, ToolCategory


class FormatAsTableTool(BaseTool):
    """Format data as a markdown table"""

    def __init__(self):
        super().__init__()
        self.category = ToolCategory.FORMATTING

    def get_description(self) -> str:
        return "Format data as a markdown table"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="data",
                type="array",
                description="List of dictionaries to format as table",
                required=True
            )
        ]

    def execute(self, data: List[Dict[str, Any]]) -> ToolResult:
        """Format as markdown table"""
        try:
            if not data:
                return ToolResult(success=True, result="(empty table)")

            # Get headers from first row
            headers = list(data[0].keys())

            # Build table
            table = "| " + " | ".join(headers) + " |\n"
            table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

            for row in data:
                values = [str(row.get(h, "")) for h in headers]
                table += "| " + " | ".join(values) + " |\n"

            return ToolResult(success=True, result=table)

        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))


class FormatAsBulletListTool(BaseTool):
    """Format items as a bullet list"""

    def __init__(self):
        super().__init__()
        self.category = ToolCategory.FORMATTING

    def get_description(self) -> str:
        return "Format items as a markdown bullet list"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="items",
                type="array",
                description="List of items to format",
                required=True
            )
        ]

    def execute(self, items: List[str]) -> ToolResult:
        """Format as bullet list"""
        try:
            formatted = "\n".join([f"- {item}" for item in items])
            return ToolResult(success=True, result=formatted)
        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))
