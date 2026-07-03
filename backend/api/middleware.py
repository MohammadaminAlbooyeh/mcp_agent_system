import time
from fastapi import Request
from backend.utils.logger import get_logger
from backend.metrics import record_api_request, record_error

logger = get_logger(__name__)


def setup_middleware(app):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        try:
            response = await call_next(request)
            elapsed = time.time() - start
            logger.info(f"{request.method} {request.url.path} - {response.status_code} ({elapsed:.2f}s)")
            try:
                record_api_request(request.url.path, request.method)
            except Exception:
                pass
            return response
        except Exception as exc:
            elapsed = time.time() - start
            try:
                record_api_request(request.url.path, request.method)
                record_error(type(exc).__name__)
            except Exception:
                pass
            logger.error(f"{request.method} {request.url.path} - ERROR ({elapsed:.2f}s): {exc}")
            raise

    @app.middleware("http")
    async def add_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(time.time())
        return response
