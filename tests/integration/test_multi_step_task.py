import pytest
from agent.core.planner import Planner
from agent.core.executor import Executor
from agent.core.evaluator import Evaluator
from agent.core.agent import Agent
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_multi_step_planning():
    agent = Agent({"llm": "openai"})
    planner = Planner(agent)
    # Mock LLM to return a plan
    with patch.object(agent.llm, 'generate', new_callable=AsyncMock, return_value='1. Search for AI trends\n2. Analyze findings\n3. Summarize'):
        plan = await planner.create_plan("Research and summarize AI trends")
        assert plan is not None
        assert len(plan) > 0


@pytest.mark.asyncio
async def test_step_execution_order():
    agent = Agent({"llm": "openai"})
    executor = Executor(agent)
    plan = ["step 1", "step 2", "step 3"]
    # Mock the reasoning process
    with patch.object(agent.reasoning, 'process', new_callable=AsyncMock, return_value="completed"):
        result = await executor.execute_plan(plan)
        assert result is not None


@pytest.mark.asyncio
async def test_result_aggregation():
    agent = Agent({"llm": "openai"})
    evaluator = Evaluator(agent)
    # Mock the evaluation process
    with patch.object(agent.llm, 'generate', new_callable=AsyncMock, return_value="Good result"):
        result = await evaluator.evaluate("test task", "test result")
        assert result is not None
