import asyncio
from agent.mcp_client.connection_manager import ConnectionManager


async def main():
    manager = ConnectionManager()
    await manager.add_connection("main", transport="stdio", command="python -m mcp_server.server")
    client = manager.get_active()
    tools = await client.list_tools()
    print(f"Connected to MCP server with {len(tools)} tools")
    await manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())
