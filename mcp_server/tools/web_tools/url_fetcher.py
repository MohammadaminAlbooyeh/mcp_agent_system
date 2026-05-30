from mcp_server.tools.base_tool import BaseTool


class URLFetcherTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "url_fetcher"
        self.description = "Fetch raw content from a URL"
        self.input_schema = {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "format": {"type": "string", "description": "Response format: text, json, html"},
            },
            "required": ["url"],
        }

    async def execute(self, url: str, format: str = "text") -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if format == "json":
                return response.text
            return response.text[:3000]
