LLM_CONFIG = {
    "openai": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 4096,
        "api_key_env": "OPENAI_API_KEY",
    },
    "claude": {
        "model": "claude-3-opus-20240229",
        "temperature": 0.7,
        "max_tokens": 4096,
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "groq": {
        "model": "mixtral-8x7b-32768",
        "temperature": 0.7,
        "max_tokens": 4096,
        "api_key_env": "GROQ_API_KEY",
    },
    "local": {
        "model": "llama2",
        "base_url": "http://localhost:11434",
        "temperature": 0.7,
    },
}
