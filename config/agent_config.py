AGENT_CONFIG = {
    "default_llm": "openai",
    "max_steps": 20,
    "max_context_tokens": 8000,
    "reasoning": {
        "chain_of_thought": True,
        "react_pattern": True,
        "self_reflection": True,
        "error_recovery": True,
    },
    "memory": {
        "short_term": {"enabled": True, "max_items": 100},
        "long_term": {"enabled": True, "storage_path": "memory_store.json"},
        "conversation": {"enabled": True, "max_messages": 100},
        "context_window": {"enabled": True, "max_tokens": 8000},
    },
    "mcp_client": {
        "transport": "stdio",
        "auto_connect": True,
        "reconnect_delay": 3,
    },
}
