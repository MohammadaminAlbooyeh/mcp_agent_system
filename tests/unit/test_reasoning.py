import pytest
from agent.reasoning.decision_maker import DecisionMaker
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_decision_maker():
    from agent.core.agent import Agent
    agent = Agent({"llm": "openai"})
    dm = DecisionMaker(agent)
    options = [
        {"name": "Option A", "description": "First option"},
        {"name": "Option B", "description": "Second option"},
    ]
    # Mock LLM to avoid API calls
    with patch.object(agent.llm, 'generate', new_callable=AsyncMock, return_value="Option A, Option B"):
        result = await dm.rank_options(options, "effectiveness")
        assert result is not None
        assert len(result) == 2
