import pytest
from mcp_server.server import MCPServer
from mcp_server.utils.config import MCPServerConfig


@pytest.fixture
def server():
    config = MCPServerConfig()
    return MCPServer(config)


def test_server_initialization(server):
    assert len(server.tools) > 0
    assert len(server.resources) > 0


def test_get_tool(server):
    tool = server.get_tool("web_search")
    assert tool is not None
    assert tool.name == "web_search"


def test_get_resource(server):
    resource = server.get_resource("database://schema")
    assert resource is not None


def test_invalid_tool(server):
    with pytest.raises(ValueError):
        server.get_tool("nonexistent_tool")
