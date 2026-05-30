class AgentError(Exception):
    pass


class ToolExecutionError(AgentError):
    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' execution failed: {message}")


class LLMError(AgentError):
    def __init__(self, provider: str, message: str):
        self.provider = provider
        super().__init__(f"LLM '{provider}' error: {message}")


class MCPConnectionError(AgentError):
    def __init__(self, message: str = "Failed to connect to MCP server"):
        super().__init__(message)


class PlanningError(AgentError):
    def __init__(self, message: str = "Failed to create execution plan"):
        super().__init__(message)
