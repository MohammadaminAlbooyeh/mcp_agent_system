import asyncio
from agent.core.agent import Agent


async def main():
    agent = Agent({"llm": "openai"})
    result = await agent.run("Generate a weekly report from the database")
    print("Report Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
