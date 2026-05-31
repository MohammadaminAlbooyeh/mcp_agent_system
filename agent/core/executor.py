from agent.utils.logger import get_logger

logger = get_logger(__name__)


class Executor:
    def __init__(self, agent):
        self.agent = agent

    async def execute_plan(self, plan: list[dict]) -> str:
        logger.info(f"Executing plan with {len(plan)} steps")
        results = []
        for step in plan:
            result = await self._execute_step(step)
            description = step.get('description') if isinstance(step, dict) else str(step)
            results.append(f"Step: {description}\nResult: {result}")
        return "\n\n".join(results)

    async def execute_tool(self, tool_name: str, params: dict = None) -> str:
        logger.info(f"Executing tool: {tool_name}")
        return await self.agent.mcp_client.call_tool(tool_name, params or {})

    async def _execute_step(self, step) -> str:
        if isinstance(step, str):
            step = {"description": step}
        if isinstance(step, dict):
            step["status"] = "in_progress"
        try:
            description = step.get("description") if isinstance(step, dict) else step
            result = await self.agent.reasoning.process(description)
            if isinstance(step, dict):
                step["status"] = "completed"
            return result
        except Exception as e:
            if isinstance(step, dict):
                step["status"] = "failed"
            return f"Error: {e}"
