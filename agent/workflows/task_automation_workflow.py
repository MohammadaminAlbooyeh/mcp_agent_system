from agent.utils.logger import get_logger

logger = get_logger(__name__)


class TaskAutomationWorkflow:
    def __init__(self, agent):
        self.agent = agent

    async def execute(self, task_description: str) -> str:
        logger.info(f"Task automation workflow for: {task_description}")
        prompt = (
            f"Break down this automation task into steps:\n{task_description}\n\n"
            "For each step, specify which tool to use and what parameters."
        )
        plan = await self.agent.llm.generate(prompt)
        results = []
        for line in plan.split("\n"):
            if "Tool:" in line and ":" in line:
                try:
                    tool_name = line.split("Tool:")[1].split(",")[0].strip()
                    result = await self.agent.executor.execute_tool(tool_name, {"query": task_description})
                    results.append(result)
                except Exception as e:
                    results.append(f"Step failed: {e}")
        return "\n".join(results)
