import json
import csv
import io
from mcp_server.tools.base_tool import BaseTool


class DataFormatterTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "data_formatter"
        self.description = "Format and convert data between different formats"
        self.input_schema = {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Input data"},
                "input_format": {"type": "string", "enum": ["json", "csv", "text"]},
                "output_format": {"type": "string", "enum": ["json", "csv", "text", "yaml"]},
            },
            "required": ["data", "input_format", "output_format"],
        }

    async def execute(self, data: str, input_format: str, output_format: str) -> str:
        if input_format == "json":
            parsed = json.loads(data)
        elif input_format == "csv":
            reader = csv.DictReader(io.StringIO(data))
            parsed = list(reader)
        else:
            parsed = data

        if output_format == "json":
            return json.dumps(parsed, indent=2)
        elif output_format == "csv":
            if isinstance(parsed, list) and parsed:
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=parsed[0].keys())
                writer.writeheader()
                writer.writerows(parsed)
                return output.getvalue()
            return str(parsed)
        elif output_format == "yaml":
            import yaml
            return yaml.dump(parsed, default_flow_style=False)
        return str(parsed)
