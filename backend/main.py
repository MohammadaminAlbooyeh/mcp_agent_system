import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.api.middleware import setup_middleware
from backend.models.database import init_db
from backend.utils.config import AppConfig
from backend.utils.logger import get_logger

logger = get_logger(__name__)

config = AppConfig()


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Initializing database...")
    init_db()
    yield


app = FastAPI(
    title="MCP Agent System API",
    description="REST API for the MCP Agent System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_middleware(app)
app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-agent-system"}


def main():
    uvicorn.run(
        "backend.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
    )


if __name__ == "__main__":
    main()
