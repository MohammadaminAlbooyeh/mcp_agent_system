from mcp_server.tools.base_tool import BaseTool


class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "web_search"
        self.description = "Search the web using Google or other search engines"
        self.input_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results (default: 10)"},
            },
            "required": ["query"],
        }

    async def execute(self, query: str, num_results: int = 10) -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.google.com/search",
                params={"q": query, "num": num_results},
                headers={"User-Agent": "Mozilla/5.0"},
            )
            return f"Search results for '{query}':\n{response.text[:2000]}"
