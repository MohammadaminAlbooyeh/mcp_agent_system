from mcp_server.tools.base_tool import BaseTool


class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "calculator"
        self.description = "Perform mathematical calculations"
        self.input_schema = {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Mathematical expression to evaluate"},
            },
            "required": ["expression"],
        }

    async def execute(self, expression: str) -> str:
        try:
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "int": int, "float": float,
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"{expression} = {result}"
        except Exception as e:
            return f"Error evaluating expression: {e}"
