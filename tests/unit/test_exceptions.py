"""
Unit tests for Exception Hierarchy - Error handling and retry policies.
"""
import pytest
from agent.utils.exceptions import (
    AgentException,
    ConfigurationError,
    MissingConfigError,
    ToolExecutionError,
    ToolTimeoutError,
    ToolAuthenticationError,
    ToolRateLimitError,
    LLMError,
    LLMRateLimitError,
    SessionExpiredError,
    ErrorSeverity,
    RetryPolicy,
)


def test_agent_exception_base():
    """Test base AgentException."""
    exc = AgentException("Test error")
    assert str(exc) == "Test error"
    assert exc.severity == ErrorSeverity.ERROR


def test_missing_config_error():
    """Test MissingConfigError."""
    exc = MissingConfigError("API_KEY not found")
    assert "API_KEY" in str(exc)
    assert exc.severity == ErrorSeverity.CRITICAL


def test_tool_execution_error_with_retry():
    """Test ToolExecutionError with retry policy."""
    retry_policy = RetryPolicy(max_retries=3, backoff_factor=2.0)
    exc = ToolExecutionError(
        "Tool failed",
        tool_name="web_search",
        retry_policy=retry_policy
    )

    assert exc.tool_name == "web_search"
    assert exc.retry_policy is not None
    assert exc.retry_policy.max_retries == 3


def test_retry_policy_exponential_backoff():
    """Test exponential backoff calculation."""
    retry_policy = RetryPolicy(
        max_retries=5,
        backoff_factor=2.0,
        strategy="exponential"
    )

    # Delays should increase exponentially
    delays = [retry_policy.get_delay(i) for i in range(3)]
    assert delays[0] < delays[1] < delays[2]


def test_retry_policy_linear_backoff():
    """Test linear backoff calculation."""
    retry_policy = RetryPolicy(
        max_retries=5,
        backoff_factor=1.0,
        strategy="linear"
    )

    delays = [retry_policy.get_delay(i) for i in range(3)]
    # Linear should increase at steady rate
    assert all(d > 0 for d in delays)


def test_tool_timeout_error():
    """Test ToolTimeoutError."""
    exc = ToolTimeoutError(
        "Web search timed out after 30s",
        tool_name="web_search",
        timeout_seconds=30
    )

    assert exc.timeout_seconds == 30
    assert exc.severity == ErrorSeverity.WARNING


def test_tool_authentication_error():
    """Test ToolAuthenticationError."""
    exc = ToolAuthenticationError(
        "Invalid API key",
        tool_name="openai_call",
        required_credentials=["api_key"]
    )

    assert exc.tool_name == "openai_call"
    assert "api_key" in exc.required_credentials
    assert exc.severity == ErrorSeverity.CRITICAL


def test_tool_rate_limit_error():
    """Test ToolRateLimitError."""
    exc = ToolRateLimitError(
        "Rate limit exceeded",
        tool_name="google_search",
        retry_after=60
    )

    assert exc.retry_after == 60
    assert exc.severity == ErrorSeverity.WARNING


def test_llm_rate_limit_error():
    """Test LLMRateLimitError with automatic retry."""
    exc = LLMRateLimitError("OpenAI rate limit hit")

    assert exc.retry_policy is not None
    # Should have exponential backoff for rate limits
    assert exc.retry_policy.max_retries > 0


def test_session_expired_error():
    """Test SessionExpiredError."""
    exc = SessionExpiredError(
        "Session expired",
        session_id="sess_123",
        ttl_minutes=60
    )

    assert exc.session_id == "sess_123"
    assert exc.ttl_minutes == 60
    assert exc.severity == ErrorSeverity.WARNING


def test_exception_to_dict():
    """Test converting exception to dictionary."""
    exc = ToolExecutionError(
        "Test tool failed",
        tool_name="test_tool"
    )

    error_dict = exc.to_dict()

    assert error_dict["message"] == "Test tool failed"
    assert error_dict["error_type"] == "ToolExecutionError"
    assert "timestamp" in error_dict
    assert error_dict.get("tool_name") == "test_tool"


def test_exception_context_tracking():
    """Test error context and metadata."""
    context = {
        "attempt": 1,
        "user_id": "user@example.com",
        "workflow": "research"
    }

    exc = ToolExecutionError(
        "Failed to execute",
        tool_name="web_search",
        context=context
    )

    assert exc.context == context


def test_severity_levels():
    """Test all error severity levels."""
    assert ErrorSeverity.CRITICAL > ErrorSeverity.ERROR
    assert ErrorSeverity.ERROR > ErrorSeverity.WARNING
    assert ErrorSeverity.WARNING > ErrorSeverity.INFO

    # Verify values
    assert ErrorSeverity.CRITICAL.value == "CRITICAL"
    assert ErrorSeverity.ERROR.value == "ERROR"
    assert ErrorSeverity.WARNING.value == "WARNING"
    assert ErrorSeverity.INFO.value == "INFO"


def test_exception_inheritance():
    """Test exception inheritance hierarchy."""
    # ToolExecutionError should be a ToolError
    exc = ToolExecutionError("Test")
    assert isinstance(exc, AgentException)

    # ToolRateLimitError should be a ToolError
    exc2 = ToolRateLimitError("Rate limit")
    assert isinstance(exc2, AgentException)


def test_exception_string_representation():
    """Test exception string representation."""
    exc = ToolExecutionError(
        "Tool failed",
        tool_name="web_search"
    )

    exc_str = str(exc)
    assert "Tool failed" in exc_str


def test_missing_config_error_variations():
    """Test various MissingConfigError scenarios."""
    # Missing single key
    exc1 = MissingConfigError("OPENAI_API_KEY")
    assert "OPENAI_API_KEY" in str(exc1)

    # Missing multiple keys
    exc2 = MissingConfigError("DATABASE_URL, REDIS_URL")
    assert "DATABASE_URL" in str(exc2) or "REDIS_URL" in str(exc2)

    # Both should be critical
    assert exc1.severity == ErrorSeverity.CRITICAL
    assert exc2.severity == ErrorSeverity.CRITICAL


def test_llm_error_variations():
    """Test various LLM error types."""
    errors = [
        ("Connection timeout", LLMError),
        ("Rate limited", LLMRateLimitError),
        ("Invalid key", LLMError),
    ]

    for message, error_class in errors:
        exc = error_class(message)
        assert exc is not None
        assert isinstance(exc, AgentException)


def test_retry_policy_max_retries():
    """Test retry policy respects max retries."""
    policy = RetryPolicy(max_retries=3)

    # Should have exactly 3 retries
    for attempt in range(3):
        delay = policy.get_delay(attempt)
        assert delay >= 0

    # Beyond max retries
    assert policy.should_retry(attempt=4) is False
