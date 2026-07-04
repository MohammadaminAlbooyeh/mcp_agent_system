from agent.core.planner import Planner
from agent.core.executor import Executor
from agent.core.evaluator import Evaluator
from agent.core.session_manager import SessionManager
from agent.memory.memory_manager import MemoryManager
from agent.reasoning.chain_of_thought import ChainOfThought
from agent.mcp_client.client import MCPClient
from agent.llm.llm_factory import LLMFactory
from agent.utils.logger import get_logger
from typing import Optional
import json

logger = get_logger(__name__)


class Agent:
    def __init__(self, config: dict = None, session_id: str = None, session_manager: SessionManager = None):
        self.config = config or {}
        self.session_id = session_id
        self.session_manager = session_manager
        self.memory = MemoryManager()
        self.planner = Planner(self)
        self.executor = Executor(self)
        self.evaluator = Evaluator(self)
        self.reasoning = ChainOfThought(self)
        self.mcp_client = MCPClient()
        self.llm = LLMFactory.create(self.config.get("llm", "openai"))
        self.history = []

    async def run(self, task: str) -> str:
        logger.info(f"Agent received task: {task}" + (f" (session: {self.session_id})" if self.session_id else ""))

        self.memory.short_term.store("current_task", task)
        context = self._build_context(task)
        plan = await self.planner.create_plan(task)
        self.memory.short_term.store("plan", plan)
        result = await self.executor.execute_plan(plan)
        evaluation = await self.evaluator.evaluate(task, result)
        self.history.append({"task": task, "plan": plan, "result": result, "evaluation": evaluation})
        await self.memory.store(task, result, memory_type="long_term")

        await self._save_session_state()
        return result

    async def restore_from_session(self) -> bool:
        if not self.session_id or not self.session_manager:
            return False

        try:
            session = await self.session_manager.get_session(self.session_id)
            if not session:
                logger.warning(f"Session not found: {self.session_id}")
                return False

            memory_snapshot = session.get("memory_snapshot", {})
            if memory_snapshot:
                self.memory.short_term._storage = memory_snapshot.get("short_term", {})
                self.memory.long_term._storage = memory_snapshot.get("long_term", {})
                logger.info(f"Restored session state from {self.session_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to restore session {self.session_id}: {e}")
            return False

        return False

    async def _save_session_state(self):
        if not self.session_id or not self.session_manager:
            return

        try:
            memory_snapshot = {
                "short_term": self.memory.short_term._storage if hasattr(self.memory.short_term, '_storage') else {},
                "long_term": self.memory.long_term._storage if hasattr(self.memory.long_term, '_storage') else {},
                "history_length": len(self.history),
            }

            await self.session_manager.save_memory_snapshot(self.session_id, memory_snapshot)
            await self.session_manager.increment_step_count(self.session_id)
            logger.debug(f"Saved session state for {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to save session state: {e}")

    def _build_context(self, task: str) -> str:
        return f"Task: {task}\nContext: {self.memory.short_term.get_all()}"

    async def get_available_tools(self) -> list:
        return await self.mcp_client.list_tools()

    @classmethod
    async def create_with_session(cls, config: dict, session_manager: SessionManager, user_id: str = None):
        session_id = await session_manager.create_session(user_id=user_id)
        agent = cls(config=config, session_id=session_id, session_manager=session_manager)
        return agent, session_id

    @classmethod
    async def restore_with_session(cls, config: dict, session_id: str, session_manager: SessionManager):
        agent = cls(config=config, session_id=session_id, session_manager=session_manager)
        await agent.restore_from_session()
        return agent
