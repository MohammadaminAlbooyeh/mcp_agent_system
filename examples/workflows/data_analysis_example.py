import asyncio
from agent.core.agent import Agent


async def main():
    agent = Agent({"llm": "openai"})
    result = await agent.run("Analyze the sales data trends from the past quarter")
    print("Analysis Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
