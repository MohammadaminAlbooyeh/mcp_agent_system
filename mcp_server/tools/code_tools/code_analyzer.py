import ast
from mcp_server.tools.base_tool import BaseTool


class CodeAnalyzerTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "code_analyzer"
        self.description = "Analyze Python code structure and complexity"
        self.input_schema = {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to analyze"},
            },
            "required": ["code"],
        }

    async def execute(self, code: str) -> str:
        try:
            tree = ast.parse(code)
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(f"{node.module}.{node.names[0].name}")
            return (
                f"Lines: {len(code.splitlines())}\n"
                f"Classes: {', '.join(classes) if classes else 'None'}\n"
                f"Functions: {', '.join(functions) if functions else 'None'}\n"
                f"Imports: {', '.join(imports) if imports else 'None'}"
            )
        except SyntaxError as e:
            return f"Syntax error: {e}"
