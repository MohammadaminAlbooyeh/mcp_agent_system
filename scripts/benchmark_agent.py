#!/usr/bin/env python3
import time
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.core.agent import Agent


async def benchmark():
    agent = Agent({"llm": "openai"})
    tasks = [
        "What is 2 + 2?",
        "What is Python?",
        "Calculate 15 * 3",
    ]
    print("Benchmarking agent performance...")
    for task in tasks:
        start = time.time()
        result = await agent.run(task)
        elapsed = time.time() - start
        print(f"  Task: '{task[:30]}...' -> {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(benchmark())
