
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from backend.utils.config import AppConfig
from backend.utils.logger import get_logger

logger = get_logger(__name__)
config = AppConfig()

engine = create_engine(
    config.database_url,
    poolclass=QueuePool,
    pool_size=20 if str(config.database_url).startswith("postgres") else 1,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
