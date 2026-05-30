import sys
from loguru import logger as loguru_logger


def get_logger(name: str = __name__):
    loguru_logger.remove()
    loguru_logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    return loguru_logger.bind(name=name)
