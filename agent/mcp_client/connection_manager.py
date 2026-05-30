from agent.mcp_client.client import MCPClient
from agent.utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, MCPClient] = {}
        self.active_connection: str = None

    async def add_connection(self, name: str, transport: str = "stdio", **kwargs):
        client = MCPClient()
        await client.connect(transport, **kwargs)
        self.connections[name] = client
        if not self.active_connection:
            self.active_connection = name
        logger.info(f"Added MCP connection: {name}")

    async def switch_connection(self, name: str):
        if name in self.connections:
            self.active_connection = name
            logger.info(f"Switched to connection: {name}")

    def get_active(self) -> MCPClient:
        if not self.active_connection:
            raise ValueError("No active connection")
        return self.connections[self.active_connection]

    async def close_all(self):
        for name, client in self.connections.items():
            await client.close()
        self.connections.clear()
        self.active_connection = None
