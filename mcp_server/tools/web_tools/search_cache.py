import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from agent.utils.logger import get_logger
from mcp_server.tools.web_tools.search_parser import SearchResultSet

logger = get_logger(__name__)


class SearchCacheBase:
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self.ttl_seconds = ttl_hours * 3600

    def _get_cache_key(self, query: str, num_results: int) -> str:
        key_string = f"{query}_{num_results}".lower().strip()
        return hashlib.md5(key_string.encode()).hexdigest()

    async def has(self, query: str, num_results: int) -> bool:
        raise NotImplementedError

    async def get(self, query: str, num_results: int) -> Optional[SearchResultSet]:
        raise NotImplementedError

    async def put(self, query: str, num_results: int, results: SearchResultSet) -> bool:
        raise NotImplementedError

    async def clear(self) -> bool:
        raise NotImplementedError


class FileSearchCache(SearchCacheBase):
    def __init__(self, cache_dir: str = "./cache/search", ttl_hours: int = 24):
        super().__init__(ttl_hours)
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, query: str, num_results: int) -> str:
        cache_key = self._get_cache_key(query, num_results)
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    async def has(self, query: str, num_results: int) -> bool:
        path = self._get_cache_path(query, num_results)
        if not os.path.exists(path):
            return False

        try:
            with open(path, "r") as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(data.get("cached_at", ""))
                age_seconds = (datetime.now() - cached_time).total_seconds()
                return age_seconds < self.ttl_seconds
        except Exception:
            return False

    async def get(self, query: str, num_results: int) -> Optional[SearchResultSet]:
        if not await self.has(query, num_results):
            return None

        try:
            path = self._get_cache_path(query, num_results)
            with open(path, "r") as f:
                data = json.load(f)

            results = [
                {
                    "url": r["url"],
                    "title": r["title"],
                    "snippet": r["snippet"],
                    "position": r["position"],
                    "domain": r["domain"],
                    "favicon_url": r.get("favicon_url"),
                    "source_type": r.get("source_type", "web"),
                }
                for r in data.get("results", [])
            ]

            return SearchResultSet(
                query=data["query"],
                results=results,
                total_results=data.get("total_results", len(results)),
                search_time_ms=data.get("search_time_ms", 0),
            )
        except Exception as e:
            logger.error(f"Failed to load from cache: {e}")
            return None

    async def put(self, query: str, num_results: int, results: SearchResultSet) -> bool:
        try:
            path = self._get_cache_path(query, num_results)

            data = {
                "query": results.query,
                "results": [
                    {
                        "url": r.url,
                        "title": r.title,
                        "snippet": r.snippet,
                        "position": r.position,
                        "domain": r.domain,
                        "favicon_url": r.favicon_url,
                        "source_type": r.source_type,
                    }
                    for r in results.results
                ],
                "total_results": results.total_results,
                "search_time_ms": results.search_time_ms,
                "cached_at": datetime.now().isoformat(),
            }

            with open(path, "w") as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")
            return False

    async def clear(self) -> bool:
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, file))
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


class InMemorySearchCache(SearchCacheBase):
    def __init__(self, ttl_hours: int = 24, max_size: int = 1000):
        super().__init__(ttl_hours)
        self.max_size = max_size
        self._cache: Dict[str, tuple] = {}  # key -> (results, timestamp)

    async def has(self, query: str, num_results: int) -> bool:
        cache_key = self._get_cache_key(query, num_results)

        if cache_key not in self._cache:
            return False

        results, timestamp = self._cache[cache_key]
        age_seconds = (datetime.now() - timestamp).total_seconds()

        if age_seconds >= self.ttl_seconds:
            del self._cache[cache_key]
            return False

        return True

    async def get(self, query: str, num_results: int) -> Optional[SearchResultSet]:
        if not await self.has(query, num_results):
            return None

        cache_key = self._get_cache_key(query, num_results)
        results, _ = self._cache[cache_key]
        return results

    async def put(self, query: str, num_results: int, results: SearchResultSet) -> bool:
        cache_key = self._get_cache_key(query, num_results)

        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        self._cache[cache_key] = (results, datetime.now())
        return True

    async def clear(self) -> bool:
        self._cache.clear()
        return True

    def size(self) -> int:
        return len(self._cache)
