from agent.utils.logger import get_logger

logger = get_logger(__name__)


class Evaluator:
    def __init__(self, agent):
        self.agent = agent

    async def evaluate(self, task: str, result: str) -> dict:
        logger.info("Evaluating result")
        prompt = (
            f"Evaluate the following result for the task: {task}\n\n"
            f"Result: {result}\n\n"
            "Rate from 1-10 and provide feedback."
        )
        evaluation = await self.agent.llm.generate(prompt)
        return {
            "task": task,
            "result_preview": result[:100],
            "evaluation": evaluation,
            "score": self._extract_score(evaluation),
        }

    def _extract_score(self, evaluation: str) -> int:
        import re
        match = re.search(r"(\d+)/10", evaluation)
        return int(match.group(1)) if match else 5
