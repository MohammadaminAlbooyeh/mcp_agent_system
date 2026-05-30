#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import init_db, engine, Base
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Initializing database...")
    init_db()
    logger.info(f"Database initialized successfully at {engine.url}")


if __name__ == "__main__":
    main()
