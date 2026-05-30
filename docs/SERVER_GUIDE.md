# MCP Server Guide

## Server Modes

### stdio Mode
```bash
python -m mcp_server.server
# Transport: stdio (default)
```

### HTTP Mode
```bash
MCP_SERVER_TRANSPORT=http python -m mcp_server.server
# Transport: http (port 8000)
```

## Architecture

The MCP Server uses:
- `mcp` Python SDK for protocol compliance
- Async tool execution for better performance
- Modular tool registration system
- Comprehensive error handling

## Adding New Tools

1. Create a new tool class in the appropriate category
2. Inherit from `BaseTool`
3. Implement the `execute` method
4. The tool is auto-registered
