import time
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionService:
    def __init__(self):
        self.executions = []

    async def execute(self, task: str, tool_calls: list[dict]) -> list[dict]:
        results = []
        for call in tool_calls:
            start = time.time()
            try:
                tool_name = call.get("tool")
                params = call.get("params", {})
                logger.info(f"Executing: {tool_name}")
                result = f"Executed {tool_name} with {params}"
                elapsed = time.time() - start
                execution = {
                    "tool": tool_name,
                    "params": params,
                    "result": result,
                    "duration": elapsed,
                    "status": "success",
                }
            except Exception as e:
                elapsed = time.time() - start
                execution = {
                    "tool": call.get("tool"),
                    "params": call.get("params", {}),
                    "result": str(e),
                    "duration": elapsed,
                    "status": "failed",
                }
            results.append(execution)
            self.executions.append(execution)
        return results
