from agent.utils.logger import get_logger

logger = get_logger(__name__)


class MCPClient:
    def __init__(self, server_url: str = None):
        self.server_url = server_url
        self.session = None
        self._tools_cache = []

    async def connect(self, transport: str = "stdio", command: str = None):
        if transport == "stdio":
            from mcp.client.stdio import stdio_client
            from mcp import ClientSession, StdioServerParameters
            params = StdioServerParameters(command=command or "python", args=["-m", "mcp_server.server"])
            self.session = await stdio_client(params)
        elif transport == "http":
            from mcp.client.http import http_client
            self.session = await http_client(self.server_url or "http://localhost:8000")
        logger.info(f"MCP Client connected via {transport}")

    async def list_tools(self) -> list:
        if not self.session:
            return self._tools_cache
        result = await self.session.list_tools()
        self._tools_cache = result.tools
        return result.tools

    async def call_tool(self, name: str, arguments: dict = None) -> str:
        if not self.session:
            return f"Not connected to MCP server"
        result = await self.session.call_tool(name, arguments or {})
        return result.content[0].text if result.content else "No output"

    async def get_resource(self, uri: str) -> str:
        if not self.session:
            return f"Not connected to MCP server"
        result = await self.session.read_resource(uri)
        return result

    async def close(self):
        if self.session:
            await self.session.close()
            logger.info("MCP Client disconnected")
