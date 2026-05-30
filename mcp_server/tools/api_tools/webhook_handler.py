from mcp_server.tools.base_tool import BaseTool


class WebhookHandlerTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "webhook_handler"
        self.description = "Send or receive webhook payloads"
        self.input_schema = {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Webhook URL"},
                "payload": {"type": "object", "description": "Webhook payload"},
                "event_type": {"type": "string", "description": "Event type header"},
            },
            "required": ["url", "payload"],
        }

    async def execute(self, url: str, payload: dict, event_type: str = "webhook") -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={"X-Event-Type": event_type},
            )
            return f"Webhook sent. Status: {response.status_code}, Response: {response.text[:500]}"
