# MCP Agent System

A production-ready AI Agent system built on the Model Context Protocol (MCP). This project demonstrates how to build a multi-tool, multi-step reasoning agent that can search the web, interact with databases, manage files, send emails, execute code, and more — all through a unified MCP interface.

## Features

- **MCP Server** with 15+ tools (web, database, file, email, API, code, utility)
- **Intelligent Agent** with multi-step reasoning (ReAct pattern)
- **Memory Management** (short-term + long-term)
- **Chain-of-Thought** reasoning with self-reflection
- **REST API** (FastAPI) for external integrations
- **React Frontend** for monitoring and control
- **Multiple LLM Support** (OpenAI, Claude, Groq, local)
- **Docker** development environment
- **Comprehensive testing** (unit, integration, load)
- **Monitoring** with Prometheus & Grafana

## Quick Start

```bash
cp .env.example .env
docker-compose up
```

## Project Structure

```
mcp_server/     - MCP Protocol server implementation
agent/          - Agent core, reasoning, memory, LLM integration
backend/        - FastAPI REST API
frontend/       - React frontend
config/         - Configuration files
docs/           - Documentation
examples/       - Usage examples
tests/          - Test suites
notebooks/      - Jupyter notebooks
scripts/        - Utility scripts
```

## Technologies

- **MCP**: mcp Python SDK
- **Backend**: FastAPI, Python
- **Agent**: OpenAI / Claude / Groq
- **Frontend**: React
- **Database**: PostgreSQL, Redis
- **Testing**: Pytest
- **Deployment**: Docker
- **Monitoring**: Prometheus, Grafana
