from mcp_server.resources.base_resource import BaseResource


class FileResource(BaseResource):
    def __init__(self):
        super().__init__()
        self.uri = "file://system"
        self.name = "File System"
        self.description = "File system access and directory listings"

    async def read(self) -> str:
        import os
        items = os.listdir(".")
        lines = ["Current directory contents:"]
        for item in items:
            if os.path.isdir(item):
                lines.append(f"  📁 {item}/")
            else:
                size = os.path.getsize(item)
                lines.append(f"  📄 {item} ({size} bytes)")
        return "\n".join(lines)
