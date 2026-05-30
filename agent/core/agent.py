from agent.core.planner import Planner
from agent.core.executor import Executor
from agent.core.evaluator import Evaluator
from agent.memory.memory_manager import MemoryManager
from agent.reasoning.chain_of_thought import ChainOfThought
from agent.mcp_client.client import MCPClient
from agent.llm.llm_factory import LLMFactory
from agent.utils.logger import get_logger

logger = get_logger(__name__)


class Agent:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.memory = MemoryManager()
        self.planner = Planner(self)
        self.executor = Executor(self)
        self.evaluator = Evaluator(self)
        self.reasoning = ChainOfThought(self)
        self.mcp_client = MCPClient()
        self.llm = LLMFactory.create(self.config.get("llm", "openai"))
        self.history = []

    async def run(self, task: str) -> str:
        logger.info(f"Agent received task: {task}")
        self.memory.short_term.store("current_task", task)
        context = self._build_context(task)
        plan = await self.planner.create_plan(task)
        self.memory.short_term.store("plan", plan)
        result = await self.executor.execute_plan(plan)
        evaluation = await self.evaluator.evaluate(task, result)
        self.history.append({"task": task, "plan": plan, "result": result, "evaluation": evaluation})
        self.memory.long_term.store(task, result)
        return result

    def _build_context(self, task: str) -> str:
        return f"Task: {task}\nContext: {self.memory.short_term.get_all()}"

    async def get_available_tools(self) -> list:
        return await self.mcp_client.list_tools()
