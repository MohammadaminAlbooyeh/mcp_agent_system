from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ToolService:
    def __init__(self):
        self._tool_registry = {}

    def register_tool(self, name: str, tool):
        self._tool_registry[name] = tool
        logger.info(f"Registered tool: {name}")

    def get_tool(self, name: str):
        return self._tool_registry.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tool_registry.keys())

    async def execute_tool(self, name: str, params: dict = None) -> str:
        tool = self.get_tool(name)
        if not tool:
            return f"Tool '{name}' not found"
        logger.info(f"Executing tool: {name}")
        return await tool.execute(**(params or {}))
