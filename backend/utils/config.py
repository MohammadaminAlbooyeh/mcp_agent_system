import os
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    host: str = field(default_factory=lambda: os.getenv("BACKEND_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("BACKEND_PORT", "8001")))
    debug: bool = field(default_factory=lambda: os.getenv("BACKEND_DEBUG", "true").lower() == "true")
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./mcp_agent.db"))
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
