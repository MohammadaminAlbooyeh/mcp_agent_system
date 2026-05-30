MCP_CONFIG = {
    "server_name": "mcp-agent-system",
    "server_version": "0.1.0",
    "transport": {
        "stdio": {"enabled": True, "default": True},
        "http": {"enabled": True, "host": "0.0.0.0", "port": 8000},
    },
    "tools": {
        "auto_register": True,
        "timeout_seconds": 60,
    },
    "resources": {
        "auto_register": True,
    },
    "logging": {
        "level": "INFO",
        "format": "detailed",
    },
}
