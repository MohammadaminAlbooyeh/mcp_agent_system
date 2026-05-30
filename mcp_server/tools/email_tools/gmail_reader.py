from mcp_server.tools.base_tool import BaseTool


class GmailReaderTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "gmail_reader"
        self.description = "Read emails from Gmail inbox"
        self.input_schema = {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Max emails to fetch"},
                "query": {"type": "string", "description": "Gmail search query"},
            },
        }

    async def execute(self, max_results: int = 10, query: str = None) -> str:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file("token.json")
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=max_results, q=query).execute()
        messages = results.get("messages", [])
        output = []
        for msg in messages[:max_results]:
            message = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
            output.append(f"From: {headers.get('From')}\nSubject: {headers.get('Subject')}\n")
        return "\n---\n".join(output)
