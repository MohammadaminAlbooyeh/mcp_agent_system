from agent.core.orchestrator import Orchestrator
from agent.workflows.research_workflow import ResearchWorkflow
from agent.workflows.analysis_workflow import AnalysisWorkflow
from agent.workflows.task_automation_workflow import TaskAutomationWorkflow
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AgentService:
    def __init__(self):
        self.orchestrator = Orchestrator()
        self._register_workflows()

    def _register_workflows(self):
        self.orchestrator.register_workflow(
            "research", ResearchWorkflow(self.orchestrator.agent)
        )
        self.orchestrator.register_workflow(
            "analysis", AnalysisWorkflow(self.orchestrator.agent)
        )
        self.orchestrator.register_workflow(
            "automation", TaskAutomationWorkflow(self.orchestrator.agent)
        )

    async def run_task(self, task: str, workflow: str = None) -> str:
        logger.info(f"Agent service running task: {task}")
        return await self.orchestrator.run_task(task, workflow)

    async def get_tools(self) -> list:
        return await self.orchestrator.agent.get_available_tools()
