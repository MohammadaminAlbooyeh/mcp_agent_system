from mcp_server.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorHandler:
    def __init__(self, server):
        self.server = server

    def handle_error(self, error: Exception) -> str:
        error_type = type(error).__name__
        error_msg = str(error)
        logger.error(f"{error_type}: {error_msg}")

        if isinstance(error, ValueError):
            return f"Invalid input: {error_msg}"
        elif isinstance(error, ConnectionError):
            return f"Connection error: {error_msg}"
        elif isinstance(error, TimeoutError):
            return f"Operation timed out: {error_msg}"
        elif isinstance(error, PermissionError):
            return f"Permission denied: {error_msg}"
        else:
            return f"An unexpected error occurred: {error_msg}"
