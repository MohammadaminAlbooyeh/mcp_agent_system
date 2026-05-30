from agent.utils.logger import get_logger

logger = get_logger(__name__)


class ToolCaller:
    def __init__(self, client):
        self.client = client

    async def call(self, tool_name: str, params: dict = None) -> str:
        logger.info(f"Calling tool: {tool_name}")
        try:
            result = await self.client.call_tool(tool_name, params or {})
            logger.debug(f"Tool result: {result[:100]}...")
            return result
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return f"Tool call error: {e}"

    async def call_multiple(self, calls: list[tuple[str, dict]]) -> list[str]:
        results = []
        for tool_name, params in calls:
            result = await self.call(tool_name, params)
            results.append(result)
        return results
