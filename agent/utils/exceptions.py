from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorSeverity(Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class RetryPolicy:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, strategy: str = "exponential"):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy

    def get_delay(self, attempt: int) -> float:
        if self.strategy == "exponential":
            delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        elif self.strategy == "linear":
            delay = min(self.base_delay * attempt, self.max_delay)
        else:
            delay = self.base_delay

        import random
        return delay + random.uniform(0, 0.1 * delay)


class AgentException(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        retry_policy: Optional[RetryPolicy] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.severity = severity
        self.retry_policy = retry_policy
        self.context = context or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }


class AgentError(AgentException):
    def __init__(self, message: str):
        super().__init__("AGENT_ERROR", message)


class ConfigurationError(AgentException):
    pass


class MissingConfigError(ConfigurationError):
    def __init__(self, config_key: str):
        super().__init__(
            "MISSING_CONFIG",
            f"Missing required configuration: {config_key}",
            ErrorSeverity.CRITICAL,
            context={"config_key": config_key},
        )


class InvalidConfigError(ConfigurationError):
    def __init__(self, config_key: str, reason: str):
        super().__init__(
            "INVALID_CONFIG",
            f"Invalid configuration for {config_key}: {reason}",
            ErrorSeverity.ERROR,
            context={"config_key": config_key, "reason": reason},
        )


class ToolError(AgentException):
    pass


class ToolNotFoundError(ToolError):
    def __init__(self, tool_name: str):
        super().__init__(
            "TOOL_NOT_FOUND",
            f"Tool not found: {tool_name}",
            ErrorSeverity.ERROR,
            context={"tool_name": tool_name},
        )


class ToolExecutionError(ToolError):
    def __init__(self, tool_name: str, message: str, retry_policy: Optional[RetryPolicy] = None):
        super().__init__(
            "TOOL_EXECUTION_ERROR",
            f"Tool '{tool_name}' execution failed: {message}",
            ErrorSeverity.ERROR,
            retry_policy=retry_policy or RetryPolicy(max_retries=3),
            context={"tool_name": tool_name, "reason": message},
        )


class ToolTimeoutError(ToolError):
    def __init__(self, tool_name: str, timeout_seconds: float):
        super().__init__(
            "TOOL_TIMEOUT",
            f"Tool execution timed out ({tool_name}): exceeded {timeout_seconds}s",
            ErrorSeverity.WARNING,
            retry_policy=RetryPolicy(max_retries=2, base_delay=2.0),
            context={"tool_name": tool_name, "timeout_seconds": timeout_seconds},
        )


class ToolAuthenticationError(ToolError):
    def __init__(self, tool_name: str, reason: str):
        super().__init__(
            "TOOL_AUTH_ERROR",
            f"Tool authentication failed ({tool_name}): {reason}",
            ErrorSeverity.ERROR,
            context={"tool_name": tool_name, "reason": reason},
        )


class ToolRateLimitError(ToolError):
    def __init__(self, tool_name: str, retry_after_seconds: int = None):
        super().__init__(
            "TOOL_RATE_LIMIT",
            f"Tool rate limit exceeded ({tool_name})",
            ErrorSeverity.WARNING,
            retry_policy=RetryPolicy(max_retries=5, base_delay=retry_after_seconds or 60),
            context={"tool_name": tool_name, "retry_after_seconds": retry_after_seconds},
        )


class LLMError(AgentException):
    def __init__(self, provider: str, message: str):
        super().__init__(
            "LLM_ERROR",
            f"LLM '{provider}' error: {message}",
            ErrorSeverity.ERROR,
            context={"provider": provider},
        )
        self.provider = provider


class LLMConnectionError(LLMError):
    def __init__(self, provider: str, reason: str):
        super().__init__(provider, f"Failed to connect: {reason}")
        self.error_code = "LLM_CONNECTION_ERROR"
        self.severity = ErrorSeverity.ERROR
        self.retry_policy = RetryPolicy(max_retries=5, base_delay=2.0)


class LLMAuthenticationError(LLMError):
    def __init__(self, provider: str):
        super().__init__(provider, "Authentication failed. Check API keys.")
        self.error_code = "LLM_AUTH_ERROR"
        self.severity = ErrorSeverity.CRITICAL


class LLMRateLimitError(LLMError):
    def __init__(self, provider: str, retry_after_seconds: int = None):
        super().__init__(provider, "Rate limit exceeded")
        self.error_code = "LLM_RATE_LIMIT"
        self.retry_policy = RetryPolicy(max_retries=5, base_delay=retry_after_seconds or 60)


class LLMContextLengthError(LLMError):
    def __init__(self, provider: str, context_length: int, max_length: int):
        super().__init__(provider, f"Context length exceeded: {context_length} > {max_length}")
        self.error_code = "LLM_CONTEXT_LENGTH"


class MCPError(AgentException):
    pass


class MCPConnectionError(MCPError):
    def __init__(self, message: str = "Failed to connect to MCP server"):
        super().__init__(
            "MCP_CONNECTION_ERROR",
            message,
            ErrorSeverity.ERROR,
            retry_policy=RetryPolicy(max_retries=3),
        )


class MCPTimeoutError(MCPError):
    def __init__(self, timeout_seconds: float):
        super().__init__(
            "MCP_TIMEOUT",
            f"MCP request timed out: exceeded {timeout_seconds}s",
            ErrorSeverity.WARNING,
            retry_policy=RetryPolicy(max_retries=2),
            context={"timeout_seconds": timeout_seconds},
        )


class MemoryError(AgentException):
    pass


class MemoryStorageError(MemoryError):
    def __init__(self, reason: str):
        super().__init__(
            "MEMORY_STORAGE_ERROR",
            f"Failed to store memory: {reason}",
            ErrorSeverity.ERROR,
            context={"reason": reason},
        )


class MemoryRetrievalError(MemoryError):
    def __init__(self, reason: str):
        super().__init__(
            "MEMORY_RETRIEVAL_ERROR",
            f"Failed to retrieve memory: {reason}",
            ErrorSeverity.ERROR,
            context={"reason": reason},
        )


class PlanningError(AgentException):
    def __init__(self, message: str = "Failed to create execution plan"):
        super().__init__(
            "PLANNING_ERROR",
            message,
            ErrorSeverity.ERROR,
        )


class PlanGenerationError(PlanningError):
    pass


class PlanExecutionError(PlanningError):
    def __init__(self, reason: str, step: int = None):
        message = f"Failed to execute plan: {reason}" + (f" at step {step}" if step else "")
        super().__init__(message)
        self.error_code = "PLAN_EXECUTION_ERROR"
        self.context = {"reason": reason, "step": step}


class SessionError(AgentException):
    pass


class SessionNotFoundError(SessionError):
    def __init__(self, session_id: str):
        super().__init__(
            "SESSION_NOT_FOUND",
            f"Session not found: {session_id}",
            ErrorSeverity.WARNING,
            context={"session_id": session_id},
        )


class SessionExpiredError(SessionError):
    def __init__(self, session_id: str):
        super().__init__(
            "SESSION_EXPIRED",
            f"Session expired: {session_id}",
            ErrorSeverity.INFO,
            context={"session_id": session_id},
        )


class RecoveryError(AgentException):
    pass


class RecoveryFailedError(RecoveryError):
    def __init__(self, reason: str, max_attempts: int):
        super().__init__(
            "RECOVERY_FAILED",
            f"Recovery failed after {max_attempts} attempts: {reason}",
            ErrorSeverity.ERROR,
            context={"reason": reason, "max_attempts": max_attempts},
        )


class UnrecoverableError(RecoveryError):
    def __init__(self, reason: str):
        super().__init__(
            "UNRECOVERABLE_ERROR",
            f"Unrecoverable error: {reason}",
            ErrorSeverity.CRITICAL,
            context={"reason": reason},
        )
