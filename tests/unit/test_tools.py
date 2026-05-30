import pytest
from mcp_server.tools.utility_tools.calculator import CalculatorTool
from mcp_server.tools.utility_tools.datetime_tool import DateTimeTool
from mcp_server.tools.utility_tools.text_processor import TextProcessorTool


@pytest.mark.asyncio
async def test_calculator():
    tool = CalculatorTool()
    result = await tool.execute(expression="2 + 2")
    assert "4" in result


@pytest.mark.asyncio
async def test_datetime_now():
    tool = DateTimeTool()
    result = await tool.execute(operation="now")
    assert result is not None


@pytest.mark.asyncio
async def test_text_processor():
    tool = TextProcessorTool()
    result = await tool.execute(text="hello", operation="uppercase")
    assert result == "HELLO"
