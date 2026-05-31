import pytest
from agent.core.agent import Agent
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_full_agent_workflow():
    agent = Agent({"llm": "openai"})
    # Mock LLM to avoid API calls
    with patch.object(agent.llm, 'generate', new_callable=AsyncMock, return_value="4"):
        result = await agent.run("What is 2 + 2?")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.asyncio
async def test_api_to_agent_pipeline():
    from backend.services.agent_service import AgentService
    with patch('agent.core.agent.Agent.run', new_callable=AsyncMock, return_value="15"):
        service = AgentService()
        result = await service.run_task("Calculate 5 * 3")
        assert result is not None
        assert isinstance(result, str)


@pytest.mark.asyncio
async def test_error_handling():
    agent = Agent({"llm": "openai"})
    # Mock LLM to handle empty task
    with patch.object(agent.llm, 'generate', new_callable=AsyncMock, return_value="No task provided"):
        result = await agent.run("")
        assert result is not None
