"""
Tool registry for discovering and executing tools
"""
from typing import Dict, List, Optional, Any
import time

from tools.base import BaseTool, ToolResult
from rag.config import TOOL_TIMEOUT_SECONDS


class ToolRegistry:
    """
    Registry for managing and executing agent tools
    """

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool"""
        self.tools[tool.name] = tool
        print(f"✓ Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI function calling schemas for all tools
        """
        return [tool.to_schema() for tool in self.tools.values()]

    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool with simple retry logic (no tenacity!)
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found"
            )

        # Simple retry logic with exponential backoff
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                start_time = time.time()

                # Execute tool
                result = tool.execute(**kwargs)

                execution_time = (time.time() - start_time) * 1000  # ms

                # If successful, return immediately
                if result.success:
                    result.execution_time_ms = execution_time
                    return result

                # If not successful and not last attempt, retry
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt)  # Exponential: 1s, 2s, 4s
                    time.sleep(wait_time)
                    continue

                return result

            except Exception as e:
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt)
                    time.sleep(wait_time)
                    continue

                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Tool execution failed after {max_attempts} attempts: {str(e)}"
                )

        # Should not reach here, but just in case
        return ToolResult(
            success=False,
            result=None,
            error=f"Tool execution failed after {max_attempts} attempts"
        )

    def describe_all_tools(self) -> str:
        """Generate description of all available tools"""
        descriptions = []
        for tool in self.tools.values():
            params = ", ".join([
                f"{p.name}: {p.type}" for p in tool.get_parameters()
            ])
            descriptions.append(
                f"- {tool.name}({params}): {tool.get_description()}"
            )
        return "\n".join(descriptions)


# Global registry instance
_global_registry = ToolRegistry()


def get_global_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return _global_registry


def register_tool(tool: BaseTool) -> None:
    """Register a tool in the global registry"""
    _global_registry.register(tool)
