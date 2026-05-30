class DecisionMaker:
    def __init__(self, agent):
        self.agent = agent

    async def decide(self, question: str, options: list[str]) -> str:
        prompt = (
            f"Decision needed: {question}\n\n"
            f"Options:\n"
            + "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
            + "\n\nAnalyze each option and recommend the best one."
        )
        return await self.agent.llm.generate(prompt)

    async def rank_options(self, options: list[dict], criteria: str) -> list[dict]:
        prompt = (
            f"Rank the following options by {criteria}:\n\n"
            + "\n".join(f"- {opt['name']}: {opt['description']}" for opt in options)
            + "\n\nReturn ranked list with explanation."
        )
        result = await self.agent.llm.generate(prompt)
        return [{"option": opt, "analysis": result} for opt in options]
