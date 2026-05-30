import pytest
from agent.reasoning.decision_maker import DecisionMaker


@pytest.mark.asyncio
async def test_decision_maker():
    from agent.core.agent import Agent
    agent = Agent({"llm": "openai"})
    dm = DecisionMaker(agent)
    options = [
        {"name": "Option A", "description": "First option"},
        {"name": "Option B", "description": "Second option"},
    ]
    result = await dm.rank_options(options, "effectiveness")
    assert result is not None
    assert len(result) == 2
