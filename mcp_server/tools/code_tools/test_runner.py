import subprocess
from mcp_server.tools.base_tool import BaseTool


class TestRunnerTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "test_runner"
        self.description = "Run Python tests using pytest"
        self.input_schema = {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Test file or directory path"},
                "verbose": {"type": "boolean", "description": "Verbose output"},
            },
            "required": ["path"],
        }

    async def execute(self, path: str, verbose: bool = False) -> str:
        cmd = ["pytest", path]
        if verbose:
            cmd.append("-v")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            return output[:2000]
        except subprocess.TimeoutExpired:
            return "Test execution timed out"
        except Exception as e:
            return f"Error running tests: {e}"
