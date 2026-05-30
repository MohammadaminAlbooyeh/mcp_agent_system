import os
import shutil
from mcp_server.tools.base_tool import BaseTool


class FileManagerTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "file_manager"
        self.description = "Manage files and directories (copy, move, delete, list)"
        self.input_schema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "copy", "move", "delete", "mkdir"],
                    "description": "Action to perform",
                },
                "source": {"type": "string", "description": "Source path"},
                "destination": {"type": "string", "description": "Destination path (for copy/move)"},
            },
            "required": ["action", "source"],
        }

    async def execute(self, action: str, source: str, destination: str = None) -> str:
        if action == "list":
            items = os.listdir(source)
            return "\n".join(items)
        elif action == "copy":
            shutil.copy2(source, destination)
            return f"Copied {source} to {destination}"
        elif action == "move":
            shutil.move(source, destination)
            return f"Moved {source} to {destination}"
        elif action == "delete":
            if os.path.isdir(source):
                shutil.rmtree(source)
            else:
                os.remove(source)
            return f"Deleted {source}"
        elif action == "mkdir":
            os.makedirs(source, exist_ok=True)
            return f"Created directory {source}"
        return f"Unknown action: {action}"
