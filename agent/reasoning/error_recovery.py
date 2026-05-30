from agent.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorRecovery:
    def __init__(self, agent):
        self.agent = agent
        self.max_retries = 3

    async def recover(self, task: str, error: str, attempt: int = 1) -> str:
        logger.info(f"Recovery attempt {attempt}/{self.max_retries} for: {task}")
        if attempt > self.max_retries:
            return f"Failed after {self.max_retries} attempts: {error}"
        prompt = (
            f"Task: {task}\n"
            f"Error encountered: {error}\n"
            f"Attempt: {attempt}/{self.max_retries}\n\n"
            "Suggest an alternative approach to fix this error."
        )
        suggestion = await self.agent.llm.generate(prompt)
        try:
            result = await self.agent.executor.execute_tool(
                suggestion.split("Action:")[1].split("\n")[0].strip()
                if "Action:" in suggestion else "web_search",
                {"query": task}
            )
            return result
        except Exception as e:
            return await self.recover(task, str(e), attempt + 1)
