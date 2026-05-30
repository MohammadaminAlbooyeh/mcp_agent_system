import asyncio
from agent.core.agent import Agent


async def main():
    agent = Agent({"llm": "openai"})
    result = await agent.run("Send a summary email of today's tasks to the team")
    print("Email Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
