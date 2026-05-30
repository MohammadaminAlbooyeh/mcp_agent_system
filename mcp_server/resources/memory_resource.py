from mcp_server.resources.base_resource import BaseResource


class MemoryResource(BaseResource):
    def __init__(self):
        super().__init__()
        self.uri = "memory://state"
        self.name = "Agent Memory State"
        self.description = "Current in-memory state of the agent"

    async def read(self) -> str:
        return (
            "Agent Memory State:\n"
            "  Active Tasks: 0\n"
            "  Memory Usage: 0 KB\n"
            "  Context Window: 0/8000 tokens\n"
            "  Last Updated: N/A"
        )
