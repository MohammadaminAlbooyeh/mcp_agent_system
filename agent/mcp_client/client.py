from agent.utils.logger import get_logger

logger = get_logger(__name__)


class MCPClient:
    def __init__(self, server_url: str = None):
        self.server_url = server_url
        self.session = None
        self._tools_cache = []
        self._stdio_transport = None
        self._session_cm = None
        self._read_stream = None
        self._write_stream = None

    async def connect(self, transport: str = "stdio", command: str = None):
        if transport == "stdio":
            from mcp.client.stdio import stdio_client
            from mcp import ClientSession, StdioServerParameters
            import sys
            params = StdioServerParameters(command=command or sys.executable, args=["-m", "mcp_server.server"])
            self._stdio_transport = stdio_client(params)
            self._read_stream, self._write_stream = await self._stdio_transport.__aenter__()
            self._session_cm = ClientSession(self._read_stream, self._write_stream)
            self.session = await self._session_cm.__aenter__()
            await self.session.initialize()
        elif transport == "http":
            from mcp.client.http import http_client
            self.session = await http_client(self.server_url or "http://localhost:8000")
            await self.session.initialize()
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
        if self._session_cm:
            await self._session_cm.__aexit__(None, None, None)
            self._session_cm = None
        if self._stdio_transport:
            await self._stdio_transport.__aexit__(None, None, None)
            self._stdio_transport = None
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("MCP Client disconnected")
