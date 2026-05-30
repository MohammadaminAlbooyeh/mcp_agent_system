from agent.utils.logger import get_logger

logger = get_logger(__name__)


class ResearchWorkflow:
    def __init__(self, agent):
        self.agent = agent

    async def execute(self, topic: str) -> str:
        logger.info(f"Research workflow started for: {topic}")
        steps = [
            {"tool": "web_search", "params": {"query": topic, "num_results": 5}},
            {"tool": "web_search", "params": {"query": f"{topic} latest news", "num_results": 5}},
        ]
        results = []
        for step in steps:
            result = await self.agent.executor.execute_tool(step["tool"], step["params"])
            results.append(result)
        prompt = (
            f"Research topic: {topic}\n\n"
            f"Search results:\n{chr(10).join(results)}\n\n"
            "Compile a comprehensive research summary with key findings and sources."
        )
        return await self.agent.llm.generate(prompt)
