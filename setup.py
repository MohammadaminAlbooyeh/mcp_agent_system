from setuptools import setup, find_packages

setup(
    name="mcp-agent-system",
    version="0.1.0",
    description="Production-ready AI Agent system built on MCP",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.25.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.0",
        "redis>=5.0.0",
        "openai>=1.3.0",
        "anthropic>=0.8.0",
    ],
)
