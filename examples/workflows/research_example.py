import asyncio
from agent.core.agent import Agent


async def main():
    agent = Agent({"llm": "openai"})
    result = await agent.run("Research the latest developments in quantum computing")
    print("Research Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
