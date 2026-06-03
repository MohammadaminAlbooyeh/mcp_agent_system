# Project Structure Overview

## Directory Tree

```
mcp_agent_system/
│
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 setup.py                     # Python package setup
├── 📄 requirements.txt             # Python dependencies
├── 📄 Dockerfile                   # Docker image definition
├── 📄 docker-compose.yml           # Multi-container development environment
├── 📄 Makefile                     # Build and utility commands
├── 📄 .env.example                 # Example environment variables
│
├── 🔧 config/                      # Configuration Management
│   ├── settings.yaml               # Main system configuration
│   ├── logging.yaml                # Logging configuration
│   ├── database.yaml               # Database configuration
│   └── llm_providers.yaml          # LLM provider settings
│
├── 🤖 agent/                       # AI Agent Core Engine
│   ├── __init__.py
│   ├── core/                       # Agent orchestration
│   │   ├── agent.py                # Main Agent class
│   │   ├── executor.py             # Task executor
│   │   ├── planner.py              # Task planning
│   │   └── state.py                # State management
│   │
│   ├── reasoning/                  # Reasoning Loop & Logic
│   │   ├── react.py                # ReAct pattern implementation
│   │   ├── chain_of_thought.py     # CoT reasoning
│   │   ├── reflection.py           # Self-reflection mechanism
│   │   └── strategies.py           # Reasoning strategies
│   │
│   ├── memory/                     # Memory Systems
│   │   ├── memory_manager.py       # Memory orchestration
│   │   ├── short_term.py           # Short-term context buffer
│   │   ├── long_term.py            # Persistent knowledge store
│   │   ├── semantic_search.py      # Vector similarity search
│   │   └── consolidation.py        # Memory consolidation
│   │
│   ├── llm/                        # LLM Integration
│   │   ├── llm_client.py           # Base LLM interface
│   │   ├── openai_client.py        # OpenAI implementation
│   │   ├── claude_client.py        # Claude implementation
│   │   ├── groq_client.py          # Groq implementation
│   │   └── local_client.py         # Local model support
│   │
│   ├── mcp_client/                 # MCP Protocol Client
│   │   ├── client.py               # MCP client implementation
│   │   ├── protocol.py             # Protocol handlers
│   │   ├── session.py              # Session management
│   │   └── discovery.py            # Tool discovery
│   │
│   ├── workflows/                  # Predefined Workflows
│   │   ├── base_workflow.py        # Base workflow class
│   │   ├── research_workflow.py    # Web research workflows
│   │   ├── analysis_workflow.py    # Data analysis workflows
│   │   ├── code_workflow.py        # Code execution workflows
│   │   └── integration_workflow.py # System integration workflows
│   │
│   └── utils/                      # Agent Utilities
│       ├── logging.py              # Structured logging
│       ├── validators.py           # Input validation
│       ├── converters.py           # Data conversion
│       └── helpers.py              # Helper functions
│
├── 🔌 mcp_server/                  # MCP Protocol Server
│   ├── __init__.py
│   ├── server.py                   # Main MCP server
│   │
│   ├── tools/                      # Tool Implementations
│   │   ├── __init__.py
│   │   ├── web_tools.py            # Web search, scraping, requests
│   │   ├── database_tools.py       # Database operations
│   │   ├── file_tools.py           # File operations
│   │   ├── email_tools.py          # Email operations
│   │   ├── code_tools.py           # Code execution
│   │   └── utility_tools.py        # Utility functions
│   │
│   ├── handlers/                   # Request Handlers
│   │   ├── tool_handler.py         # Tool invocation
│   │   ├── resource_handler.py     # Resource management
│   │   └── prompt_handler.py       # Prompt handling
│   │
│   ├── resources/                  # Resource Definitions
│   │   ├── web_resources.py        # Web resource schemas
│   │   ├── db_resources.py         # Database resource schemas
│   │   └── code_resources.py       # Code resource schemas
│   │
│   ├── prompts/                    # System Prompts
│   │   ├── system_prompt.txt       # Base system prompt
│   │   ├── tool_prompt.txt         # Tool description prompts
│   │   ├── examples.txt            # Usage examples
│   │   └── constraints.txt         # Behavioral constraints
│   │
│   └── utils/                      # Server Utilities
│       ├── validators.py           # Request validation
│       ├── serializers.py          # Response serialization
│       └── error_handlers.py       # Error handling
│
├── ⚡ backend/                     # FastAPI REST API
│   ├── __init__.py
│   ├── main.py                     # FastAPI application factory
│   │
│   ├── api/                        # API Routes
│   │   ├── v1/                     # API v1 endpoints
│   │   │   ├── tasks.py            # Task management endpoints
│   │   │   ├── agents.py           # Agent control endpoints
│   │   │   ├── tools.py            # Tool discovery endpoints
│   │   │   ├── memory.py           # Memory query endpoints
│   │   │   ├── metrics.py          # Metrics endpoints
│   │   │   └── health.py           # Health check endpoints
│   │   │
│   │   ├── websocket.py            # WebSocket connections
│   │   ├── middleware.py           # Custom middleware
│   │   └── dependencies.py         # Dependency injection
│   │
│   ├── models/                     # Pydantic Data Models
│   │   ├── task.py                 # Task schemas
│   │   ├── agent.py                # Agent schemas
│   │   ├── tool.py                 # Tool schemas
│   │   ├── memory.py               # Memory schemas
│   │   └── responses.py            # Response schemas
│   │
│   ├── services/                   # Business Logic
│   │   ├── task_service.py         # Task management service
│   │   ├── agent_service.py        # Agent orchestration service
│   │   ├── tool_service.py         # Tool management service
│   │   ├── memory_service.py       # Memory service
│   │   └── monitoring_service.py   # Monitoring service
│   │
│   ├── database/                   # Database Layer
│   │   ├── connection.py           # Connection pooling
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── migrations/             # Database migrations (Alembic)
│   │   └── schemas.py              # Database schemas
│   │
│   └── utils/                      # Backend Utilities
│       ├── authentication.py       # Auth utilities
│       ├── validators.py           # Data validation
│       ├── decorators.py           # Custom decorators
│       └── helpers.py              # Helper functions
│
├── 🎨 frontend/                    # React Frontend
│   ├── public/                     # Static assets
│   │   ├── index.html              # Main HTML
│   │   ├── favicon.ico
│   │   └── manifest.json
│   │
│   └── src/                        # React Source Code
│       ├── index.tsx               # Entry point
│       ├── App.tsx                 # Root component
│       ├── vite.config.ts          # Vite configuration
│       │
│       ├── pages/                  # Page components
│       │   ├── Dashboard.tsx       # Main dashboard
│       │   ├── Tasks.tsx           # Task management
│       │   ├── Monitoring.tsx      # Monitoring view
│       │   ├── Agents.tsx          # Agent control
│       │   ├── Tools.tsx           # Tool explorer
│       │   └── Settings.tsx        # System settings
│       │
│       ├── components/             # Reusable components
│       │   ├── TaskCard.tsx        # Task display
│       │   ├── AgentStatus.tsx     # Agent status indicator
│       │   ├── ToolList.tsx        # Tool list view
│       │   ├── MemoryBrowser.tsx   # Memory visualization
│       │   ├── MetricsChart.tsx    # Metrics chart
│       │   └── Layout.tsx          # Page layout
│       │
│       ├── hooks/                  # Custom React hooks
│       │   ├── useAgent.ts         # Agent interaction
│       │   ├── useTasks.ts         # Task management
│       │   ├── useWebSocket.ts     # WebSocket connection
│       │   └── useMetrics.ts       # Metrics fetching
│       │
│       ├── services/               # API services
│       │   ├── api.ts              # HTTP client
│       │   ├── taskService.ts      # Task API calls
│       │   ├── agentService.ts     # Agent API calls
│       │   └── metricsService.ts   # Metrics API calls
│       │
│       ├── types/                  # TypeScript types
│       │   ├── agent.ts            # Agent types
│       │   ├── task.ts             # Task types
│       │   └── api.ts              # API response types
│       │
│       ├── styles/                 # CSS/Styling
│       │   ├── globals.css         # Global styles
│       │   └── components.css      # Component styles
│       │
│       └── utils/                  # Frontend utilities
│           ├── formatters.ts       # Data formatting
│           └── helpers.ts          # Helper functions
│
├── 📊 monitoring/                  # Observability
│   ├── prometheus/                 # Prometheus config
│   │   └── prometheus.yml
│   │
│   ├── grafana_dashboards/         # Grafana dashboards
│   │   ├── agent_metrics.json      # Agent metrics dashboard
│   │   ├── api_performance.json    # API performance dashboard
│   │   ├── system_health.json      # System health dashboard
│   │   └── tool_usage.json         # Tool usage dashboard
│   │
│   └── alerts/                     # Alert rules
│       └── rules.yml               # Prometheus alert rules
│
├── 📚 docs/                        # Documentation
│   ├── README.md                   # Documentation index
│   ├── QUICKSTART.md               # Getting started guide
│   ├── ARCHITECTURE.md             # Architecture guide
│   ├── ARCHITECTURE_DIAGRAM.html   # Interactive diagrams
│   ├── PROJECT_STRUCTURE.md        # This file
│   ├── MCP_GUIDE.md                # MCP protocol guide
│   ├── AGENT_GUIDE.md              # Agent usage guide
│   ├── TOOLS_GUIDE.md              # Tools reference
│   ├── RESOURCES_GUIDE.md          # Resources reference
│   ├── SERVER_GUIDE.md             # Server setup guide
│   ├── API_REFERENCE.md            # REST API reference
│   ├── DEPLOYMENT.md               # Deployment guide
│   ├── TROUBLESHOOTING.md          # Troubleshooting guide
│   └── images/                     # Documentation images
│
├── 🧪 tests/                       # Test Suites
│   ├── conftest.py                 # Pytest configuration
│   │
│   ├── unit/                       # Unit Tests
│   │   ├── test_agent.py           # Agent tests
│   │   ├── test_reasoning.py       # Reasoning tests
│   │   ├── test_memory.py          # Memory tests
│   │   ├── test_llm_client.py      # LLM client tests
│   │   ├── test_mcp_client.py      # MCP client tests
│   │   ├── test_tools.py           # Tool tests
│   │   └── test_api.py             # API tests
│   │
│   ├── integration/                # Integration Tests
│   │   ├── test_agent_flow.py      # End-to-end agent flow
│   │   ├── test_mcp_integration.py # MCP integration
│   │   ├── test_api_integration.py # API integration
│   │   ├── test_database.py        # Database integration
│   │   └── test_cache.py           # Cache integration
│   │
│   └── load/                       # Load Testing
│       ├── conftest.py             # Load test config
│       ├── test_concurrent_tasks.py # Concurrency tests
│       ├── test_api_load.py        # API load tests
│       └── test_agent_load.py      # Agent load tests
│
├── 📓 notebooks/                   # Jupyter Notebooks
│   ├── agent_tutorial.ipynb        # Agent usage tutorial
│   ├── tool_exploration.ipynb      # Tool exploration
│   ├── memory_analysis.ipynb       # Memory analysis
│   ├── performance_profiling.ipynb # Performance profiling
│   └── examples/                   # Example notebooks
│
├── 💾 examples/                    # Usage Examples
│   ├── basic/                      # Basic examples
│   │   ├── simple_task.py          # Simple task execution
│   │   ├── web_search.py           # Web search example
│   │   └── database_query.py       # Database query example
│   │
│   ├── advanced/                   # Advanced examples
│   │   ├── research_workflow.py    # Research automation
│   │   ├── data_analysis.py        # Data analysis pipeline
│   │   ├── code_generation.py      # Code generation
│   │   └── custom_tools.py         # Custom tool creation
│   │
│   └── workflows/                  # Predefined workflows
│       ├── market_research.py      # Market research workflow
│       ├── document_analysis.py    # Document analysis
│       ├── api_integration.py      # API integration
│       └── report_generation.py    # Report generation
│
├── 🔧 scripts/                     # Utility Scripts
│   ├── setup_database.py           # Database setup
│   ├── seed_data.py                # Seed test data
│   ├── migrate_data.py             # Data migration
│   ├── backup_database.py          # Backup utilities
│   ├── performance_test.py         # Performance testing
│   ├── docker_build.sh             # Docker build script
│   └── deploy.sh                   # Deployment script
│
└── .github/                        # GitHub Configuration
    ├── workflows/                  # CI/CD workflows
    │   ├── tests.yml               # Test CI workflow
    │   ├── deploy.yml              # Deployment workflow
    │   └── codeql.yml              # Code analysis
    │
    └── ISSUE_TEMPLATE/             # Issue templates
        ├── bug_report.md
        ├── feature_request.md
        └── documentation.md
```

## Component Dependencies

### Core Dependencies
```
Agent Core
├── Reasoning Engine
│   └── LLM Clients (OpenAI, Claude, Groq, Local)
├── Memory System
│   └── Database (PostgreSQL, Redis)
├── MCP Client
│   └── MCP Server
│       └── Tools (Web, DB, File, Email, Code, Utils)
└── Workflows
    └── Tool Orchestration
```

### API Dependencies
```
FastAPI Application
├── Task Service
│   └── Agent Core
├── Agent Service
│   └── Agent Core
├── Tool Service
│   └── MCP Server
├── Memory Service
│   └── Memory System
└── Monitoring Service
    └── Prometheus Metrics
```

## Key Statistics

- **Total Directories**: 38+
- **Core Modules**: 5 (agent, mcp_server, backend, frontend, config)
- **Tools Available**: 15+
- **API Endpoints**: 20+
- **Test Suites**: 3 (unit, integration, load)
- **Documentation Files**: 10+
- **Supported LLM Providers**: 4+ (OpenAI, Claude, Groq, Local)

## Build & Deployment

### Local Development
```bash
docker-compose up
```
Starts all services with PostgreSQL, Redis, and the application.

### Production Deployment
- Kubernetes manifests in `k8s/` (if present)
- Docker images built and pushed to registry
- Environment configuration via `.env` file
- Database migrations handled automatically

## Configuration Hierarchy

1. **Environment Variables** (.env) - Highest priority
2. **Configuration Files** (config/*.yaml)
3. **Docker Compose** (docker-compose.yml)
4. **Code Defaults** - Lowest priority

## Adding New Components

### New Tool
1. Implement in `mcp_server/tools/`
2. Register in MCP server
3. Add tests in `tests/unit/test_tools.py`
4. Document in `docs/TOOLS_GUIDE.md`

### New API Endpoint
1. Add route in `backend/api/v1/`
2. Create service in `backend/services/`
3. Add Pydantic model in `backend/models/`
4. Add tests in `tests/unit/test_api.py`
5. Document in `docs/API_REFERENCE.md`

### New Workflow
1. Create in `agent/workflows/`
2. Add usage example in `examples/workflows/`
3. Add notebook in `notebooks/examples/`
4. Document in `docs/AGENT_GUIDE.md`

---

For more details, see the comprehensive documentation in the `docs/` directory.
