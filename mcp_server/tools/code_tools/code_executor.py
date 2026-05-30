import sys
import io
from mcp_server.tools.base_tool import BaseTool


class CodeExecutorTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "code_executor"
        self.description = "Execute Python code in a sandboxed environment"
        self.input_schema = {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"},
                "timeout": {"type": "integer", "description": "Execution timeout in seconds"},
            },
            "required": ["code"],
        }

    async def execute(self, code: str, timeout: int = 30) -> str:
        stdout = io.StringIO()
        stderr = io.StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = stdout
        sys.stderr = stderr
        try:
            exec_globals = {"__builtins__": __builtins__}
            exec(code, exec_globals)
            output = stdout.getvalue()
            if stderr.getvalue():
                output += "\nStderr:\n" + stderr.getvalue()
            return output or "Code executed successfully (no output)"
        except Exception as e:
            return f"Error: {e}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
