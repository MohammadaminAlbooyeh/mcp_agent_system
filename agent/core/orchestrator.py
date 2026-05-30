from agent.core.agent import Agent
from agent.utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    def __init__(self, config: dict = None):
        self.agent = Agent(config)
        self.workflows = {}

    async def run_task(self, task: str, workflow: str = None) -> str:
        logger.info(f"Orchestrator running task with workflow: {workflow}")
        if workflow and workflow in self.workflows:
            return await self.workflows[workflow].execute(task)
        return await self.agent.run(task)

    async def run_multi_step(self, tasks: list[str]) -> list[str]:
        results = []
        for task in tasks:
            result = await self.run_task(task)
            results.append(result)
        return results

    def register_workflow(self, name: str, workflow):
        self.workflows[name] = workflow
