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
            results.append(f"Step: {step['description']}\nResult: {result}")
        return "\n\n".join(results)

    async def execute_tool(self, tool_name: str, params: dict = None) -> str:
        logger.info(f"Executing tool: {tool_name}")
        return await self.agent.mcp_client.call_tool(tool_name, params or {})

    async def _execute_step(self, step: dict) -> str:
        step["status"] = "in_progress"
        try:
            result = await self.agent.reasoning.process(step["description"])
            step["status"] = "completed"
            return result
        except Exception as e:
            step["status"] = "failed"
            return f"Error: {e}"
