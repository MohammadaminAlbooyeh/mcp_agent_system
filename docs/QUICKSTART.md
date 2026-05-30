# Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

## Installation

1. Clone the repository
2. Copy environment file: `cp .env.example .env`
3. Install Python dependencies: `pip install -r requirements.txt`
4. Install frontend dependencies: `cd frontend && npm install`
5. Start the application: `docker-compose up`

Or run locally:
```bash
python -m mcp_server.server
uvicorn backend.main:app
cd frontend && npm start
```

## First Task

Send a task to the agent:
```bash
curl -X POST http://localhost:8001/api/agents/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Hello, what can you do?"}'
```
