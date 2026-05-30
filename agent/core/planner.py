from agent.utils.logger import get_logger

logger = get_logger(__name__)


class Planner:
    def __init__(self, agent):
        self.agent = agent

    async def create_plan(self, task: str) -> list[dict]:
        logger.info(f"Creating plan for: {task}")
        tools = await self.agent.get_available_tools()
        prompt = (
            f"Create a step-by-step plan for: {task}\n\n"
            f"Available tools: {[t.name for t in tools]}\n\n"
            "Return a list of steps, each with action and expected outcome."
        )
        response = await self.agent.llm.generate(prompt)
        plan = self._parse_plan(response)
        return plan

    def _parse_plan(self, response: str) -> list[dict]:
        steps = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                steps.append({"description": line, "status": "pending"})
        return steps if steps else [{"description": response, "status": "pending"}]
