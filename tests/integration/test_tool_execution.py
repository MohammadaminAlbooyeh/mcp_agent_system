import pytest
from mcp_server.tools.utility_tools.calculator import CalculatorTool
from mcp_server.tools.utility_tools.datetime_tool import DateTimeTool
from mcp_server.tools.utility_tools.text_processor import TextProcessorTool


@pytest.mark.asyncio
async def test_web_search_tool():
    from mcp_server.tools.web_tools.web_search import WebSearchTool
    tool = WebSearchTool()
    result = await tool.execute(query="test query", num_results=3)
    assert result is not None
    assert "test query" in result


@pytest.mark.asyncio
async def test_database_tool():
    from mcp_server.tools.database_tools.sql_executor import SQLExecutorTool
    tool = SQLExecutorTool()
    result = await tool.execute(query="SELECT 1")
    assert result is not None


@pytest.mark.asyncio
async def test_file_tool():
    from mcp_server.tools.file_tools.file_reader import FileReaderTool
    import tempfile
    import os
    tool = FileReaderTool()
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("test content")
        test_file = f.name
    try:
        result = await tool.execute(path=test_file, format="txt")
        assert result == "test content"
    finally:
        os.unlink(test_file)


@pytest.mark.asyncio
async def test_calculator_tool():
    tool = CalculatorTool()
    result = await tool.execute(expression="2 + 2")
    assert "4" in result


@pytest.mark.asyncio
async def test_datetime_tool():
    tool = DateTimeTool()
    result = await tool.execute(operation="now")
    assert result is not None


@pytest.mark.asyncio
async def test_text_processor_tool():
    tool = TextProcessorTool()
    result = await tool.execute(text="hello world", operation="uppercase")
    assert result == "HELLO WORLD"
