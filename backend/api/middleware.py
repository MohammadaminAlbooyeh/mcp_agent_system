import time
from fastapi import Request
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def setup_middleware(app):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start
        logger.info(f"{request.method} {request.url.path} - {response.status_code} ({elapsed:.2f}s)")
        return response

    @app.middleware("http")
    async def add_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(time.time())
        return response
