from mcp_server.tools.base_tool import BaseTool


class FileReaderTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "file_reader"
        self.description = "Read files in various formats (PDF, TXT, CSV, DOCX)"
        self.input_schema = {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "format": {"type": "string", "enum": ["txt", "pdf", "csv", "docx"]},
            },
            "required": ["path"],
        }

    async def execute(self, path: str, format: str = "txt") -> str:
        if format == "txt":
            with open(path, "r") as f:
                return f.read()
        elif format == "csv":
            import pandas as pd
            df = pd.read_csv(path)
            return df.to_string()
        elif format == "pdf":
            from pypdf import PdfReader
            reader = PdfReader(path)
            return "\n".join(page.extract_text() for page in reader.pages)
        elif format == "docx":
            from docx import Document
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs)
        return "Unsupported format"
