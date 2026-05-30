import os


class Settings:
    APP_NAME = "MCP Agent System"
    APP_VERSION = "0.1.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mcp_agent.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))
    MCP_SERVER_TRANSPORT = os.getenv("MCP_SERVER_TRANSPORT", "stdio")

    AGENT_DEFAULT_LLM = os.getenv("AGENT_DEFAULT_LLM", "openai")
    AGENT_MAX_STEPS = int(os.getenv("AGENT_MAX_STEPS", "20"))
    AGENT_MAX_CONTEXT_TOKENS = int(os.getenv("AGENT_MAX_CONTEXT_TOKENS", "8000"))

    BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8001"))


settings = Settings()
