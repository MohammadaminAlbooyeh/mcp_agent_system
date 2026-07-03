import os
import json
from typing import Optional, Any
from redis import Redis, ConnectionPool
from redis.exceptions import RedisError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._pool = None
        return cls._instance

    def init(self, url: Optional[str] = None):
        url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self._pool = ConnectionPool.from_url(url)
            self._client = Redis(connection_pool=self._pool)
            self._client.ping()
            logger.info(f"Redis connected: {url}")
        except Exception as exc:
            logger.warning(f"Redis connection failed: {exc}")
            self._client = None
            self._pool = None

    @property
    def client(self) -> Optional[Redis]:
        return getattr(self, "_client", None)

    def get(self, key: str) -> Optional[str]:
        try:
            if self.client:
                return self.client.get(key)
        except RedisError as exc:
            logger.warning(f"Redis get failed for {key}: {exc}")
        return None

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        try:
            if self.client:
                if not isinstance(value, str):
                    value = json.dumps(value)
                return bool(self.client.set(key, value, ex=ex))
        except RedisError as exc:
            logger.warning(f"Redis set failed for {key}: {exc}")
        return False

    def delete(self, key: str) -> bool:
        try:
            if self.client:
                return bool(self.client.delete(key))
        except RedisError as exc:
            logger.warning(f"Redis delete failed for {key}: {exc}")
        return False

    def exists(self, key: str) -> bool:
        try:
            if self.client:
                return bool(self.client.exists(key))
        except RedisError as exc:
            logger.warning(f"Redis exists check failed for {key}: {exc}")
        return False


_redis_client = RedisClient()

def get_redis_client() -> RedisClient:
    if _redis_client.client is None:
        _redis_client.init()
    return _redis_client
