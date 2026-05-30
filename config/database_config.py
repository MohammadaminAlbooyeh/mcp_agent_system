DATABASE_CONFIG = {
    "default": {
        "url": "sqlite:///./mcp_agent.db",
        "echo": False,
        "pool_size": 5,
        "max_overflow": 10,
    },
    "postgres": {
        "url_env": "DATABASE_URL",
        "echo": False,
        "pool_size": 10,
        "max_overflow": 20,
    },
    "redis": {
        "url_env": "REDIS_URL",
        "decode_responses": True,
    },
}
