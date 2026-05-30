from mcp_server.tools.base_tool import BaseTool


class HTTPClientTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "http_client"
        self.description = "Make HTTP requests to external services"
        self.input_schema = {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Request URL"},
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                "headers": {"type": "object", "description": "Request headers"},
                "body": {"type": "object", "description": "Request body"},
            },
            "required": ["url"],
        }

    async def execute(self, url: str, method: str = "GET", headers: dict = None, body: dict = None) -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, json=body)
            return f"Status: {response.status_code}\nBody: {response.text[:2000]}"
