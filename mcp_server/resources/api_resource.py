from mcp_server.resources.base_resource import BaseResource


class APIResource(BaseResource):
    def __init__(self):
        super().__init__()
        self.uri = "api://endpoints"
        self.name = "API Endpoints"
        self.description = "Available REST API endpoints"

    async def read(self) -> str:
        return (
            "Available API Endpoints:\n"
            "  POST /api/agents/run\n"
            "  GET  /api/tasks\n"
            "  GET  /api/tasks/{id}\n"
            "  POST /api/tasks\n"
            "  GET  /api/tools\n"
            "  GET  /api/executions\n"
            "  GET  /api/monitoring/metrics"
        )
