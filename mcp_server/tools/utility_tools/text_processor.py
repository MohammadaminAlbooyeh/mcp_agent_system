from mcp_server.tools.base_tool import BaseTool


class TextProcessorTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "text_processor"
        self.description = "Process and transform text content"
        self.input_schema = {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to process"},
                "operation": {
                    "type": "string",
                    "enum": ["uppercase", "lowercase", "title", "reverse", "count_words", "count_chars", "split", "join", "trim"],
                    "description": "Operation to perform",
                },
                "delimiter": {"type": "string", "description": "Delimiter for split/join operations"},
            },
            "required": ["text", "operation"],
        }

    async def execute(self, text: str, operation: str, delimiter: str = None) -> str:
        if operation == "uppercase":
            return text.upper()
        elif operation == "lowercase":
            return text.lower()
        elif operation == "title":
            return text.title()
        elif operation == "reverse":
            return text[::-1]
        elif operation == "count_words":
            return f"Word count: {len(text.split())}"
        elif operation == "count_chars":
            return f"Character count: {len(text)}"
        elif operation == "split":
            parts = text.split(delimiter) if delimiter else text.split()
            return "\n".join(f"{i}: {p}" for i, p in enumerate(parts))
        elif operation == "trim":
            return text.strip()
        return f"Unknown operation: {operation}"
