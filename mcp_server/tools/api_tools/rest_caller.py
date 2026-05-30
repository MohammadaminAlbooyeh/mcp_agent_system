from mcp_server.tools.base_tool import BaseTool


class RESTCallerTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "rest_caller"
        self.description = "Call REST API endpoints with full control"
        self.input_schema = {
            "type": "object",
            "properties": {
                "endpoint": {"type": "string", "description": "API endpoint URL"},
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                "headers": {"type": "object", "description": "Custom headers"},
                "params": {"type": "object", "description": "Query parameters"},
                "data": {"type": "object", "description": "Request payload"},
            },
            "required": ["endpoint"],
        }

    async def execute(self, endpoint: str, method: str = "GET", headers: dict = None, params: dict = None, data: dict = None) -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.request(method, endpoint, headers=headers, params=params, json=data)
            return f"[{response.status_code}] {response.text[:2000]}"
