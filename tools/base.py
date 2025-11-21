"""
Base interface for agent tools
All tools must inherit from BaseTool
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ToolCategory(Enum):
    """Tool categories for organization"""
    SEARCH = "search"
    CALCULATION = "calculation"
    FORMATTING = "formatting"
    UTILITY = "utility"
    INFORMATION = "information"


@dataclass
class ToolParameter:
    """Tool parameter specification"""
    name: str
    type: str  # "string", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Optional[Any] = None
    items_type: Optional[str] = None  # For array types: specify element type ("string", "object", "number", etc.)


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class BaseTool(ABC):
    """
    Abstract base class for all agent tools
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.category = ToolCategory.UTILITY

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters
        Must be implemented by subclasses
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return human-readable description of what the tool does"""
        pass

    @abstractmethod
    def get_parameters(self) -> list[ToolParameter]:
        """Return list of parameters the tool accepts"""
        pass

    def to_schema(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI function calling schema
        """
        parameters_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for param in self.get_parameters():
            param_schema = {
                "type": param.type,
                "description": param.description
            }

            # Add items field for array types (required by OpenAI/JSON Schema)
            if param.type == "array" and param.items_type:
                param_schema["items"] = {"type": param.items_type}

            parameters_schema["properties"][param.name] = param_schema

            if param.default is not None:
                parameters_schema["properties"][param.name]["default"] = param.default
            if param.required:
                parameters_schema["required"].append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.get_description(),
                "parameters": parameters_schema
            }
        }

    def __str__(self) -> str:
        return f"{self.name}: {self.get_description()}"
