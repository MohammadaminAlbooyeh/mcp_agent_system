# API Reference

## Endpoints

### POST /api/agents/run
Run an agent task.

Request:
```json
{
  "task": "Research quantum computing",
  "workflow": "research"
}
```

### GET /api/tasks
List all tasks.

### POST /api/tasks
Create a new task.

### GET /api/tasks/{id}
Get task details.

### GET /api/tools
List available MCP tools.

### GET /api/executions
List execution history.

### GET /api/monitoring/metrics
Get system metrics.

## Response Format

All endpoints return JSON with appropriate HTTP status codes.
