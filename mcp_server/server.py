import asyncio
import json
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from mcp_server.tools.base_tool import BaseTool
from mcp_server.tools.web_tools.web_search import WebSearchTool
from mcp_server.tools.web_tools.web_scraper import WebScraperTool
from mcp_server.tools.web_tools.url_fetcher import URLFetcherTool
from mcp_server.tools.database_tools.sql_executor import SQLExecutorTool
from mcp_server.tools.database_tools.db_reader import DBReaderTool
from mcp_server.tools.database_tools.db_writer import DBWriterTool
from mcp_server.tools.file_tools.file_reader import FileReaderTool
from mcp_server.tools.file_tools.file_writer import FileWriterTool
from mcp_server.tools.file_tools.file_manager import FileManagerTool
from mcp_server.tools.email_tools.gmail_reader import GmailReaderTool
from mcp_server.tools.email_tools.gmail_sender import GmailSenderTool
from mcp_server.tools.email_tools.email_parser import EmailParserTool
from mcp_server.tools.api_tools.http_client import HTTPClientTool
from mcp_server.tools.api_tools.rest_caller import RESTCallerTool
from mcp_server.tools.api_tools.webhook_handler import WebhookHandlerTool
from mcp_server.tools.code_tools.code_executor import CodeExecutorTool
from mcp_server.tools.code_tools.code_analyzer import CodeAnalyzerTool
from mcp_server.tools.code_tools.test_runner import TestRunnerTool
from mcp_server.tools.utility_tools.calculator import CalculatorTool
from mcp_server.tools.utility_tools.datetime_tool import DateTimeTool
from mcp_server.tools.utility_tools.text_processor import TextProcessorTool
from mcp_server.tools.utility_tools.data_formatter import DataFormatterTool

from mcp_server.resources.base_resource import BaseResource
from mcp_server.resources.database_resource import DatabaseResource
from mcp_server.resources.file_resource import FileResource
from mcp_server.resources.api_resource import APIResource
from mcp_server.resources.memory_resource import MemoryResource

from mcp_server.handlers.tool_handler import ToolHandler
from mcp_server.handlers.resource_handler import ResourceHandler
from mcp_server.handlers.error_handler import ErrorHandler

from mcp_server.utils.config import MCPServerConfig
from mcp_server.utils.logger import get_logger

logger = get_logger(__name__)


class MCPServer:
    def __init__(self, config: MCPServerConfig = None):
        self.config = config or MCPServerConfig()
        self.server = Server("mcp-agent-system")
        self.tools: dict[str, BaseTool] = {}
        self.resources: dict[str, BaseResource] = {}
        self.tool_handler = ToolHandler(self)
        self.resource_handler = ResourceHandler(self)
        self.error_handler = ErrorHandler(self)
        self._register_tools()
        self._register_resources()
        self._setup_handlers()

    def _register_tools(self):
        tool_classes = [
            WebSearchTool, WebScraperTool, URLFetcherTool,
            SQLExecutorTool, DBReaderTool, DBWriterTool,
            FileReaderTool, FileWriterTool, FileManagerTool,
            GmailReaderTool, GmailSenderTool, EmailParserTool,
            HTTPClientTool, RESTCallerTool, WebhookHandlerTool,
            CodeExecutorTool, CodeAnalyzerTool, TestRunnerTool,
            CalculatorTool, DateTimeTool, TextProcessorTool, DataFormatterTool,
        ]
        for tool_cls in tool_classes:
            tool = tool_cls()
            self.tools[tool.name] = tool

    def _register_resources(self):
        resource_classes = [
            DatabaseResource, FileResource, APIResource, MemoryResource,
        ]
        for resource_cls in resource_classes:
            resource = resource_cls()
            self.resources[resource.uri] = resource

    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [tool.to_mcp_tool() for tool in self.tools.values()]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            return await self.tool_handler.handle_tool_call(name, arguments)

        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            return [resource.to_mcp_resource() for resource in self.resources.values()]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            return await self.resource_handler.handle_resource_request(uri)

    async def run(self):
        transport = self.config.transport
        if transport == "stdio":
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="mcp-agent-system",
                        server_version="0.1.0",
                    ),
                )
        elif transport == "http":
            from mcp.server import http
            async with http.http_server(self.server, self.config.host, self.config.port):
                await asyncio.Event().wait()

    def get_tool(self, name: str) -> BaseTool:
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        return tool

    def get_resource(self, uri: str) -> BaseResource:
        resource = self.resources.get(uri)
        if not resource:
            raise ValueError(f"Resource '{uri}' not found")
        return resource


def main():
    config = MCPServerConfig()
    server = MCPServer(config)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
