import time
from mcp_server.resources.base_resource import BaseResource


class MemoryResource(BaseResource):
    _start_time = time.time()
    _active_tasks = 0
    _memory_usage_kb = 0
    _context_tokens = 0

    def __init__(self):
        super().__init__()
        self.uri = "memory://state"
        self.name = "Agent Memory State"
        self.description = "Current in-memory state of the agent"

    @classmethod
    def track_task_start(cls):
        cls._active_tasks += 1

    @classmethod
    def track_task_end(cls):
        cls._active_tasks = max(0, cls._active_tasks - 1)

    @classmethod
    def update_memory(cls, usage_kb: int, context_tokens: int):
        cls._memory_usage_kb = usage_kb
        cls._context_tokens = context_tokens

    async def read(self) -> str:
        import psutil
        process = psutil.Process()
        mem_info = process.memory_info()
        uptime_seconds = int(time.time() - self._start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return (
            f"Agent Memory State:\n"
            f"  Uptime: {hours}h {minutes}m {seconds}s\n"
            f"  Active Tasks: {self._active_tasks}\n"
            f"  Memory Usage: {mem_info.rss / 1024:.0f} KB\n"
            f"  Context Window: {self._context_tokens}/8000 tokens\n"
            f"  Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
