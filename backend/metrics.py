from prometheus_client import Counter, Histogram, Gauge, start_http_server
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize Prometheus metrics
TASKS_TOTAL = Counter(
    'mcp_agent_tasks_total',
    'Total number of tasks processed',
    ['status']
)

TASK_DURATION = Histogram(
    'mcp_agent_task_duration_seconds',
    'Task execution duration in seconds'
)

TOOL_CALLS_TOTAL = Counter(
    'mcp_agent_tool_calls_total',
    'Total number of tool calls',
    ['tool_name', 'status']
)

TOOL_CALL_DURATION = Histogram(
    'mcp_agent_tool_call_duration_seconds',
    'Tool call duration in seconds',
    ['tool_name']
)

AGENT_REQUESTS_TOTAL = Counter(
    'mcp_agent_requests_total',
    'Total API requests received',
    ['endpoint', 'method']
)

ACTIVE_AGENT_RUNS = Gauge(
    'mcp_agent_active_runs',
    'Number of currently active agent runs'
)

errors_total = Counter(
    'mcp_agent_errors_total',
    'Total errors',
    ['error_type']
)


def increment_task_completed(duration_seconds: float = 0.0):
    TASKS_TOTAL.labels(status="completed").inc()
    if duration_seconds:
        TASK_DURATION.observe(duration_seconds)


def increment_task_failed():
    TASKS_TOTAL.labels(status="failed").inc()


def record_tool_call(tool_name: str, duration_seconds: float, status: str = "success"):
    TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status=status).inc()
    TOOL_CALL_DURATION.labels(tool_name=tool_name).observe(duration_seconds)


def record_api_request(endpoint: str, method: str):
    AGENT_REQUESTS_TOTAL.labels(endpoint=endpoint, method=method).inc()


def set_active_runs(count: int):
    ACTIVE_AGENT_RUNS.set(count)


def record_error(error_type: str = "unknown"):
    errors_total.labels(error_type=error_type).inc()


class MetricsServer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._server_started = False
        return cls._instance

    def start_metrics_server(self, port: int = 8002):
        if not self._server_started:
            try:
                start_http_server(port)
                logger.info(f"Prometheus metrics server started on :{port}/metrics")
                self._server_started = True
            except OSError:
                logger.warning(f"Metrics server already running on :{port}")
