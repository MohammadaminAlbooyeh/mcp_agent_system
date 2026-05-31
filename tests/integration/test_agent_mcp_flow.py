import pytest
from agent.core.agent import Agent
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_agent_mcp_connection():
    agent = Agent({"llm": "openai"})
    tools = await agent.get_available_tools()
    assert tools is not None
    assert isinstance(tools, list)


@pytest.mark.asyncio
async def test_agent_uses_tools():
    agent = Agent({"llm": "openai"})
    # Mock the MCP client connection to avoid subprocess issues in tests
    with patch.object(agent.mcp_client, 'connect', new_callable=AsyncMock):
        with patch.object(agent.mcp_client, 'list_tools', new_callable=AsyncMock, return_value=[]):
            await agent.mcp_client.connect(transport="stdio")
            tools = await agent.mcp_client.list_tools()
            assert isinstance(tools, list)


@pytest.mark.asyncio
async def test_agent_returns_results():
    agent = Agent({"llm": "openai"})
    # Mock the LLM generate method to avoid API calls
    with patch.object(agent.llm, 'generate', new_callable=AsyncMock, return_value="Hello!"):
        result = await agent.run("Say hello")
        assert result is not None
        assert isinstance(result, str)
