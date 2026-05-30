from mcp_server.tools.base_tool import BaseTool


class WeatherTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "weather"
        self.description = "Get weather information for a city"
        self.input_schema = {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
            },
            "required": ["city"],
        }

    async def execute(self, city: str) -> str:
        return f"Weather information for {city}: Sunny, 72°F"
