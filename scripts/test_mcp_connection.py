#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.mcp_client.client import MCPClient


async def main():
    client = MCPClient()
    print("Testing MCP connection...")
    tools = await client.list_tools()
    if tools:
        print(f"Connected! Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    else:
        print("No tools found. Make sure MCP server is running.")
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
