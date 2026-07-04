from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from agent.utils.logger import get_logger

logger = get_logger(__name__)


class Memory:
    def __init__(self, key: str, value: Any, timestamp: datetime = None, metadata: dict = None):
        self.key = key
        self.value = value
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        self.access_count = 0
        self.last_accessed = self.timestamp

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "metadata": self.metadata,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if isinstance(self.last_accessed, datetime) else self.last_accessed,
        }


class RetrievalStrategy(ABC):
    @abstractmethod
    async def retrieve(self, query: str, memory_storage: Dict[str, Memory], context: dict = None) -> List[Memory]:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class KeywordStrategy(RetrievalStrategy):
    async def retrieve(self, query: str, memory_storage: Dict[str, Memory], context: dict = None) -> List[Memory]:
        results = []
        query_lower = query.lower()

        for key, memory in memory_storage.items():
            if query_lower in key.lower():
                results.append(memory)
            else:
                value_str = str(memory.value).lower()
                if query_lower in value_str:
                    results.append(memory)

        return sorted(results, key=lambda m: m.access_count, reverse=True)[:10]

    def get_name(self) -> str:
        return "keyword"


class RecentFirstStrategy(RetrievalStrategy):
    async def retrieve(self, query: str, memory_storage: Dict[str, Memory], context: dict = None) -> List[Memory]:
        query_lower = query.lower()
        results = []

        for key, memory in memory_storage.items():
            if query_lower in key.lower() or query_lower in str(memory.value).lower():
                results.append(memory)

        return sorted(results, key=lambda m: m.timestamp, reverse=True)[:10]

    def get_name(self) -> str:
        return "recent_first"


class RelevanceDecayStrategy(RetrievalStrategy):
    async def retrieve(self, query: str, memory_storage: Dict[str, Memory], context: dict = None) -> List[Memory]:
        query_lower = query.lower()
        now = datetime.now()
        results = []

        for key, memory in memory_storage.items():
            if query_lower in key.lower() or query_lower in str(memory.value).lower():
                age_hours = (now - memory.timestamp).total_seconds() / 3600
                decay_factor = 1.0 / (1.0 + age_hours / 24.0)
                relevance_score = memory.access_count * decay_factor

                results.append((memory, relevance_score))

        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:10]]

    def get_name(self) -> str:
        return "relevance_decay"


class SemanticStrategy(RetrievalStrategy):
    def __init__(self, embedding_service=None, vector_store=None):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def retrieve(self, query: str, memory_storage: Dict[str, Memory], context: dict = None) -> List[Memory]:
        if not self.embedding_service or not self.vector_store:
            logger.warning("Semantic retrieval requires embedding service and vector store")
            keyword_strategy = KeywordStrategy()
            return await keyword_strategy.retrieve(query, memory_storage, context)

        try:
            query_embedding = await self.embedding_service.embed_text(query)
            search_results = await self.vector_store.search(query_embedding, top_k=10)

            memories = []
            for result in search_results:
                if result.id in memory_storage:
                    memory = memory_storage[result.id]
                    memory.metadata["similarity_score"] = result.similarity_score
                    memories.append(memory)

            return memories
        except Exception as e:
            logger.error(f"Semantic retrieval failed: {e}, falling back to keyword")
            keyword_strategy = KeywordStrategy()
            return await keyword_strategy.retrieve(query, memory_storage, context)

    def get_name(self) -> str:
        return "semantic"


class HybridStrategy(RetrievalStrategy):
    def __init__(self, embedding_service=None, vector_store=None):
        self.keyword_strategy = KeywordStrategy()
        self.semantic_strategy = SemanticStrategy(embedding_service, vector_store)

    async def retrieve(self, query: str, memory_storage: Dict[str, Memory], context: dict = None) -> List[Memory]:
        try:
            keyword_results = await self.keyword_strategy.retrieve(query, memory_storage, context)
            semantic_results = await self.semantic_strategy.retrieve(query, memory_storage, context)

            combined = {}
            for mem in keyword_results:
                combined[mem.key] = (mem, 0.5)

            for mem in semantic_results:
                if mem.key in combined:
                    combined[mem.key] = (mem, combined[mem.key][1] + 0.5)
                else:
                    combined[mem.key] = (mem, 0.5)

            results = sorted(combined.values(), key=lambda x: x[1], reverse=True)
            return [r[0] for r in results[:10]]
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            return await self.keyword_strategy.retrieve(query, memory_storage, context)

    def get_name(self) -> str:
        return "hybrid"


class StrategySelector:
    def __init__(self, embedding_service=None, vector_store=None):
        self.strategies = {
            "keyword": KeywordStrategy(),
            "recent_first": RecentFirstStrategy(),
            "relevance_decay": RelevanceDecayStrategy(),
            "semantic": SemanticStrategy(embedding_service, vector_store),
            "hybrid": HybridStrategy(embedding_service, vector_store),
        }
        self.default_strategy = "hybrid" if embedding_service and vector_store else "keyword"

    async def retrieve(self, query: str, memory_storage: Dict[str, Memory], strategy: str = "auto", context: dict = None) -> List[Memory]:
        if strategy == "auto":
            strategy = self.default_strategy

        selected_strategy = self.strategies.get(strategy, self.strategies[self.default_strategy])
        return await selected_strategy.retrieve(query, memory_storage, context)

    def get_available_strategies(self) -> List[str]:
        return list(self.strategies.keys())

    def set_default_strategy(self, strategy: str):
        if strategy in self.strategies:
            self.default_strategy = strategy
            logger.info(f"Default retrieval strategy set to: {strategy}")
