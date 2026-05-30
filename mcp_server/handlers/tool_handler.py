from mcp_server.utils.logger import get_logger

logger = get_logger(__name__)


class ToolHandler:
    def __init__(self, server):
        self.server = server

    async def handle_tool_call(self, name: str, arguments: dict) -> list:
        from mcp.types import TextContent
        try:
            tool = self.server.get_tool(name)
            logger.info(f"Executing tool: {name} with args: {arguments}")
            result = await tool.execute(**arguments)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [TextContent(type="text", text=f"Error: {e}")]
