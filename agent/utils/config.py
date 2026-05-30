import os
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    llm_provider: str = field(default_factory=lambda: os.getenv("AGENT_DEFAULT_LLM", "openai"))
    max_steps: int = field(default_factory=lambda: int(os.getenv("AGENT_MAX_STEPS", "20")))
    max_context_tokens: int = field(default_factory=lambda: int(os.getenv("AGENT_MAX_CONTEXT_TOKENS", "8000")))
    mcp_transport: str = field(default_factory=lambda: os.getenv("MCP_SERVER_TRANSPORT", "stdio"))
    mcp_server_url: str = field(default_factory=lambda: os.getenv("MCP_SERVER_URL", "http://localhost:8000"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
