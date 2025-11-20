"""
Tools module - Initialize and register all tools
"""
from tools.registry import get_global_registry, register_tool
from tools.rag_tools import SearchVectorDBTool, GetCollectionStatsTool
from tools.utility_tools import CalculatorTool, GetCurrentDateTool
from tools.formatting_tools import FormatAsTableTool, FormatAsBulletListTool


def initialize_tools():
    """Register all available tools"""
    # RAG tools
    register_tool(SearchVectorDBTool())
    register_tool(GetCollectionStatsTool())

    # Utility tools
    register_tool(CalculatorTool())
    register_tool(GetCurrentDateTool())

    # Formatting tools
    register_tool(FormatAsTableTool())
    register_tool(FormatAsBulletListTool())


# Auto-initialize on import
initialize_tools()


__all__ = [
    "get_global_registry",
    "register_tool",
    "initialize_tools"
]
