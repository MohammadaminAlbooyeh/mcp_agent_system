from datetime import datetime, timedelta
from mcp_server.tools.base_tool import BaseTool


class DateTimeTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "datetime_tool"
        self.description = "Get current date/time and perform date calculations"
        self.input_schema = {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["now", "format", "add", "subtract", "diff"],
                    "description": "Date/time operation",
                },
                "date": {"type": "string", "description": "Input date (YYYY-MM-DD)"},
                "days": {"type": "integer", "description": "Days to add/subtract"},
                "format": {"type": "string", "description": "Output format"},
            },
            "required": ["operation"],
        }

    async def execute(self, operation: str, date: str = None, days: int = None, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        now = datetime.now()
        if operation == "now":
            return now.strftime(format)
        elif operation == "format":
            dt = datetime.strptime(date, "%Y-%m-%d") if date else now
            return dt.strftime(format)
        elif operation == "add":
            dt = datetime.strptime(date, "%Y-%m-%d") if date else now
            return (dt + timedelta(days=days or 0)).strftime(format)
        elif operation == "subtract":
            dt = datetime.strptime(date, "%Y-%m-%d") if date else now
            return (dt - timedelta(days=days or 0)).strftime(format)
        return f"Unknown operation: {operation}"
