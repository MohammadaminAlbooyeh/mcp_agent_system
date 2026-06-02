import time
import importlib
import pkgutil
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionService:
    def __init__(self):
        self.executions = []
        self._tool_registry = {}
        self._discover_tools()

    def _discover_tools(self):
        import mcp_server.tools as tools_pkg
        for importer, modname, ispkg in pkgutil.walk_packages(tools_pkg.__path__, f"{tools_pkg.__name__}."):
            try:
                module = importlib.import_module(modname)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and attr.__name__ != "BaseTool":
                        from mcp_server.tools.base_tool import BaseTool
                        if issubclass(attr, BaseTool) and attr is not BaseTool:
                            tool_instance = attr()
                            self._tool_registry[tool_instance.name] = tool_instance
            except Exception:
                pass

    async def execute(self, task: str, tool_calls: list[dict]) -> list[dict]:
        results = []
        for call in tool_calls:
            start = time.time()
            try:
                tool_name = call.get("tool")
                params = call.get("params", {})
                logger.info(f"Executing: {tool_name}")
                tool = self._tool_registry.get(tool_name)
                if tool:
                    result = await tool.execute(**params)
                else:
                    result = f"Tool '{tool_name}' not found in registry"
                elapsed = time.time() - start
                execution = {
                    "tool": tool_name,
                    "params": params,
                    "result": result,
                    "duration": elapsed,
                    "status": "success",
                }
            except Exception as e:
                elapsed = time.time() - start
                execution = {
                    "tool": call.get("tool"),
                    "params": call.get("params", {}),
                    "result": str(e),
                    "duration": elapsed,
                    "status": "failed",
                }
            results.append(execution)
            self.executions.append(execution)
        return results
