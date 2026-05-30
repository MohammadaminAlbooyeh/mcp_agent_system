#!/usr/bin/env python3
from mcp_server.server import MCPServer
from mcp_server.utils.config import MCPServerConfig


def main():
    config = MCPServerConfig()
    server = MCPServer(config)
    print(f"MCP Server: {config.transport}://{config.host}:{config.port}")
    print(f"\nRegistered Tools ({len(server.tools)}):")
    for name, tool in sorted(server.tools.items()):
        print(f"  - {name}: {tool.description}")
    print(f"\nRegistered Resources ({len(server.resources)}):")
    for uri, resource in server.resources.items():
        print(f"  - {uri}: {resource.description}")


if __name__ == "__main__":
    main()
