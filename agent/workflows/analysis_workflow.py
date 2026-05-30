from agent.utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisWorkflow:
    def __init__(self, agent):
        self.agent = agent

    async def execute(self, data_source: str) -> str:
        logger.info(f"Analysis workflow started for: {data_source}")
        if data_source.endswith(".csv"):
            data = await self.agent.executor.execute_tool("file_reader", {"path": data_source, "format": "csv"})
        elif data_source.startswith("http"):
            data = await self.agent.executor.execute_tool("url_fetcher", {"url": data_source})
        else:
            data = data_source
        prompt = (
            f"Analyze the following data:\n\n{data[:2000]}\n\n"
            "Provide:\n"
            "1. Summary of the data\n"
            "2. Key patterns and insights\n"
            "3. Statistical findings\n"
            "4. Recommendations"
        )
        return await self.agent.llm.generate(prompt)
