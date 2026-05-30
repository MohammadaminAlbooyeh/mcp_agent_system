import os
from dataclasses import dataclass, field


@dataclass
class MCPServerConfig:
    host: str = field(default_factory=lambda: os.getenv("MCP_SERVER_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("MCP_SERVER_PORT", "8000")))
    transport: str = field(default_factory=lambda: os.getenv("MCP_SERVER_TRANSPORT", "stdio"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    max_tool_timeout: int = field(default_factory=lambda: int(os.getenv("MCP_MAX_TOOL_TIMEOUT", "60")))
