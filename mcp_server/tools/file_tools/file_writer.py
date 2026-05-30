from mcp_server.tools.base_tool import BaseTool


class FileWriterTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "file_writer"
        self.description = "Write content to files"
        self.input_schema = {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content to write"},
                "mode": {"type": "string", "enum": ["write", "append"], "description": "Write or append mode"},
            },
            "required": ["path", "content"],
        }

    async def execute(self, path: str, content: str, mode: str = "write") -> str:
        file_mode = "w" if mode == "write" else "a"
        with open(path, file_mode) as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
