import pytest
import asyncio
import time
from mcp_server.tools.utility_tools.calculator import CalculatorTool
from mcp_server.tools.utility_tools.datetime_tool import DateTimeTool
from mcp_server.tools.utility_tools.text_processor import TextProcessorTool


@pytest.mark.asyncio
async def test_concurrent_tool_calls():
    tool = CalculatorTool()
    tasks = [tool.execute(expression=f"{i} + {i}") for i in range(10)]
    start = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    assert len(results) == 10
    assert elapsed < 30
    for i, result in enumerate(results):
        assert str(i * 2) in result


@pytest.mark.asyncio
async def test_memory_usage():
    import tracemalloc
    from unittest.mock import AsyncMock, patch
    tracemalloc.start()
    agent_config = {"llm": "openai"}
    from agent.core.agent import Agent
    agent = Agent(agent_config)
    # Mock LLM to avoid API calls
    with patch.object(agent.llm, 'generate', new_callable=AsyncMock, return_value="result"):
        await agent.run("test")
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 500 * 1024 * 1024


@pytest.mark.asyncio
async def test_response_times():
    tool = DateTimeTool()
    call_times = []
    for _ in range(5):
        start = time.time()
        await tool.execute(operation="now")
        call_times.append(time.time() - start)
    avg_time = sum(call_times) / len(call_times)
    assert avg_time < 5.0


@pytest.mark.asyncio
async def test_tool_throughput():
    tool = TextProcessorTool()
    start = time.time()
    batch = 20
    tasks = [tool.execute(text=f"item {i}", operation="uppercase") for i in range(batch)]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    throughput = batch / elapsed
    assert throughput > 0
    assert len(results) == batch
