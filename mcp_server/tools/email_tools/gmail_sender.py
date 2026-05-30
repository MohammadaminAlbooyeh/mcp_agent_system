from mcp_server.tools.base_tool import BaseTool


class GmailSenderTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "gmail_sender"
        self.description = "Send emails via Gmail"
        self.input_schema = {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body"},
            },
            "required": ["to", "subject", "body"],
        }

    async def execute(self, to: str, subject: str, body: str) -> str:
        import base64
        from email.message import EmailMessage
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file("token.json")
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["Subject"] = subject
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": encoded}).execute()
        return f"Email sent to {to}"
