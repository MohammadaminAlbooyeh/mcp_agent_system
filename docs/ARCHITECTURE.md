# Architecture

## System Design

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend  │────▶│   Backend    │────▶│  MCP Server  │
│   (React)   │     │  (FastAPI)   │     │   (Python)   │
└─────────────┘     └──────────────┘     └──────────────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────┐     ┌──────────────┐
                    │   Agent      │     │   Tools      │
                    │  (Core)      │     │  (22 tools)  │
                    └──────────────┘     └──────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
             ┌──────────┐  ┌──────────┐
             │  Memory   │  │  LLM     │
             │ Manager   │  │ Factory  │
             └──────────┘  └──────────┘
```

## Data Flow

1. User submits task via Frontend or API
2. Backend routes to Agent Service
3. Agent creates plan using LLM
4. Agent executes steps via MCP tools
5. Results stored in memory
6. Final response returned to user

## Components

- **Frontend**: React SPA with routing
- **Backend**: FastAPI REST API
- **MCP Server**: Tool execution layer
- **Agent**: Core intelligence
- **Memory**: Short/long-term storage
- **LLM**: Multi-provider support
