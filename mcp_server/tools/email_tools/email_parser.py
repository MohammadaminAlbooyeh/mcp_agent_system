from mcp_server.tools.base_tool import BaseTool


class EmailParserTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "email_parser"
        self.description = "Parse email content and extract structured data"
        self.input_schema = {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Raw email content"},
            },
            "required": ["content"],
        }

    async def execute(self, content: str) -> str:
        from email import message_from_string
        msg = message_from_string(content)
        parsed = {
            "from": msg["From"],
            "to": msg["To"],
            "subject": msg["Subject"],
            "date": msg["Date"],
            "body": "",
        }
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    parsed["body"] = part.get_payload(decode=True).decode()
                    break
        else:
            parsed["body"] = msg.get_payload(decode=True).decode()
        return "\n".join(f"{k}: {v}" for k, v in parsed.items())
