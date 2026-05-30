from agent.utils.logger import get_logger

logger = get_logger(__name__)


class ChainOfThought:
    def __init__(self, agent):
        self.agent = agent

    async def process(self, step: str) -> str:
        logger.info(f"Chain of thought processing: {step}")
        prompt = (
            f"Think through this step step by step:\n{step}\n\n"
            "Consider:\n"
            "1. What is the goal?\n"
            "2. What information do I have?\n"
            "3. What tools should I use?\n"
            "4. What is the expected outcome?"
        )
        return await self.agent.llm.generate(prompt)
