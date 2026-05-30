from abc import ABC, abstractmethod
from typing import Any
import mcp.types as types


class BaseTool(ABC):
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.input_schema: dict = {}

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        pass

    def to_mcp_tool(self) -> types.Tool:
        return types.Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema,
        )

    def format_result(self, result: Any) -> str:
        if isinstance(result, str):
            return result
        return str(result)
