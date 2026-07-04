from agent.memory.short_term_memory import ShortTermMemory
from agent.memory.long_term_memory import LongTermMemory
from agent.memory.conversation_history import ConversationHistory
from agent.memory.context_window import ContextWindow
from agent.memory.embedding_service import EmbeddingService
from agent.memory.vector_store import FAISSVectorStore, InMemoryVectorStore
from agent.utils.logger import get_logger
from typing import List, Tuple, Optional

logger = get_logger(__name__)


class MemoryManager:
    def __init__(self, use_semantic: bool = True, embedding_provider: str = "local", vector_store_type: str = "faiss"):
        self.short_term = ShortTermMemory()

        embedding_service = None
        vector_store = None

        if use_semantic:
            try:
                embedding_service = EmbeddingService(provider=embedding_provider, use_cache=True)
                if vector_store_type == "faiss":
                    vector_store = FAISSVectorStore(dimension=embedding_service.get_dimension())
                else:
                    vector_store = InMemoryVectorStore(dimension=embedding_service.get_dimension())
                logger.info(f"Semantic memory enabled with {embedding_provider} embeddings")
            except Exception as e:
                logger.warning(f"Failed to initialize semantic memory: {e}")

        self.long_term = LongTermMemory(embedding_service=embedding_service, vector_store=vector_store)
        self.conversation = ConversationHistory()
        self.context = ContextWindow()
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def store(self, key: str, value: any, memory_type: str = "short_term", metadata: dict = None):
        if memory_type == "short_term":
            self.short_term.store(key, value)
        elif memory_type == "long_term":
            await self.long_term.store(key, value, metadata=metadata)
        elif memory_type == "conversation":
            self.conversation.add(value)
        logger.debug(f"Stored in {memory_type}: {key}")

    def retrieve(self, key: str, memory_type: str = "short_term") -> any:
        if memory_type == "short_term":
            return self.short_term.retrieve(key)
        elif memory_type == "long_term":
            return self.long_term.retrieve(key)
        return None

    async def search(self, query: str, memory_type: str = "long_term", strategy: str = "auto", limit: int = 10) -> List[Tuple[str, any]]:
        if memory_type == "long_term":
            return await self.long_term.search(query, strategy=strategy, limit=limit)
        return []

    async def semantic_search(self, query: str, top_k: int = 5) -> List[Tuple[str, any, float]]:
        return await self.long_term.semantic_search(query, top_k=top_k)

    async def batch_store(self, items: List[dict]) -> int:
        return await self.long_term.batch_store(items)

    def clear_short_term(self):
        self.short_term.clear()
        logger.info("Short-term memory cleared")

    def get_statistics(self) -> dict:
        return {
            "short_term": len(self.short_term._storage) if hasattr(self.short_term, '_storage') else 0,
            "long_term": self.long_term.get_statistics(),
            "conversation": len(self.conversation.history) if hasattr(self.conversation, 'history') else 0,
        }
