import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from agent.memory.retrieval_strategy import Memory, StrategySelector
from agent.utils.logger import get_logger

logger = get_logger(__name__)


class LongTermMemory:
    def __init__(self, storage_path: str = "memory_store.json", embedding_service=None, vector_store=None):
        self.storage_path = storage_path
        self._storage = {}
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.strategy_selector = StrategySelector(embedding_service, vector_store)
        self._load()

    def _load(self) -> dict:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        self._storage[key] = Memory(key=key, value=value)
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
        return self._storage

    def _save(self):
        try:
            data = {key: mem.value for key, mem in self._storage.items()}
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    async def store(self, key: str, value: any, metadata: dict = None):
        memory = Memory(key=key, value=value, metadata=metadata)
        self._storage[key] = memory

        if self.embedding_service and self.vector_store:
            try:
                embedding = await self.embedding_service.embed_text(str(value))
                await self.vector_store.store(key, str(value), embedding, metadata)
            except Exception as e:
                logger.error(f"Failed to store embedding: {e}")

        self._save()

    def retrieve(self, key: str) -> any:
        memory = self._storage.get(key)
        if memory:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            return memory.value
        return None

    async def search(self, query: str, strategy: str = "auto", limit: int = 10) -> List[Tuple[str, any]]:
        memories = await self.strategy_selector.retrieve(query, self._storage, strategy=strategy)
        results = []

        for memory in memories[:limit]:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            results.append((memory.key, memory.value))

        return results

    async def semantic_search(self, query: str, top_k: int = 5) -> List[Tuple[str, any, float]]:
        if not self.embedding_service or not self.vector_store:
            logger.warning("Semantic search requires embedding service and vector store")
            keyword_results = await self.search(query, strategy="keyword", limit=top_k)
            return [(k, v, 0.0) for k, v in keyword_results]

        try:
            query_embedding = await self.embedding_service.embed_text(query)
            search_results = await self.vector_store.search(query_embedding, top_k=top_k)

            results = []
            for result in search_results:
                if result.id in self._storage:
                    memory = self._storage[result.id]
                    memory.access_count += 1
                    memory.last_accessed = datetime.now()
                    results.append((result.id, memory.value, result.similarity_score))

            return results
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    async def batch_store(self, items: List[Dict[str, Any]]) -> int:
        count = 0
        for item in items:
            key = item.get("key")
            value = item.get("value")
            metadata = item.get("metadata")

            if key and value:
                await self.store(key, value, metadata)
                count += 1

        return count

    def get_all(self) -> dict:
        return {key: mem.value for key, mem in self._storage.items()}

    def clear(self):
        self._storage.clear()
        if self.vector_store:
            try:
                self.vector_store.clear()
            except Exception as e:
                logger.error(f"Failed to clear vector store: {e}")
        self._save()

    def get_statistics(self) -> dict:
        return {
            "total_memories": len(self._storage),
            "vector_store_size": self.vector_store.size() if self.vector_store else 0,
            "embedding_service_available": self.embedding_service is not None,
            "retrieval_strategies": self.strategy_selector.get_available_strategies(),
        }
