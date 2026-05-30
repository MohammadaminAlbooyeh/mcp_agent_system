from agent.utils.logger import get_logger

logger = get_logger(__name__)


class Reflection:
    def __init__(self, agent):
        self.agent = agent

    async def reflect(self, task: str, result: str) -> str:
        prompt = (
            f"Review the following execution:\n\n"
            f"Task: {task}\n"
            f"Result: {result}\n\n"
            "Reflect on:\n"
            "1. Was the approach correct?\n"
            "2. Are there any errors or improvements?\n"
            "3. What could be done differently?\n"
            "4. Is the result complete and accurate?"
        )
        return await self.agent.llm.generate(prompt)

    async def correct(self, task: str, result: str, feedback: str) -> str:
        prompt = (
            f"Original task: {task}\n"
            f"Previous result: {result}\n"
            f"Feedback: {feedback}\n\n"
            "Provide a corrected/improved version."
        )
        return await self.agent.llm.generate(prompt)
