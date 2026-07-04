import os
from typing import List, Optional
from abc import ABC, abstractmethod
from agent.utils.logger import get_logger
import numpy as np

logger = get_logger(__name__)


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        pass

    @abstractmethod
    async def batch_embed(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.dimension = 1536  # text-embedding-3-small dimension
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            logger.error("OpenAI client not available")
            self.client = None

    async def embed(self, text: str) -> List[float]:
        if not self.client or not self.api_key:
            logger.warning("OpenAI embedding not available, using fallback")
            return await LocalEmbeddingProvider().embed(text)

        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to embed with OpenAI: {e}")
            return await LocalEmbeddingProvider().embed(text)

    async def batch_embed(self, texts: List[str]) -> List[List[float]]:
        if not self.client or not self.api_key:
            logger.warning("OpenAI embedding not available, using fallback")
            local_provider = LocalEmbeddingProvider()
            return await local_provider.batch_embed(texts)

        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Failed to batch embed with OpenAI: {e}")
            local_provider = LocalEmbeddingProvider()
            return await local_provider.batch_embed(texts)

    def get_dimension(self) -> int:
        return self.dimension


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model_name = model
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model, trust_remote_code=True)
        except ImportError:
            logger.error("sentence-transformers not available")
            self.model = None

    async def embed(self, text: str) -> List[float]:
        if not self.model:
            logger.warning("Local embedding model not available")
            return self._fallback_embedding(text)

        try:
            embedding = self.model.encode(text)
            return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        except Exception as e:
            logger.error(f"Failed to embed with local model: {e}")
            return self._fallback_embedding(text)

    async def batch_embed(self, texts: List[str]) -> List[List[float]]:
        if not self.model:
            logger.warning("Local embedding model not available")
            return [self._fallback_embedding(text) for text in texts]

        try:
            embeddings = self.model.encode(texts)
            return [e.tolist() if hasattr(e, 'tolist') else list(e) for e in embeddings]
        except Exception as e:
            logger.error(f"Failed to batch embed with local model: {e}")
            return [self._fallback_embedding(text) for text in texts]

    def get_dimension(self) -> int:
        return self.dimension

    def _fallback_embedding(self, text: str) -> List[float]:
        hash_value = hash(text)
        np.random.seed(abs(hash_value) % (2**32))
        return np.random.randn(self.dimension).tolist()


class EmbeddingCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache = {}
        self._access_order = []

    def get(self, text: str) -> Optional[List[float]]:
        if text in self._cache:
            self._access_order.remove(text)
            self._access_order.append(text)
            return self._cache[text]
        return None

    def put(self, text: str, embedding: List[float]):
        if text in self._cache:
            self._access_order.remove(text)
        elif len(self._cache) >= self.max_size:
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]

        self._cache[text] = embedding
        self._access_order.append(text)

    def clear(self):
        self._cache.clear()
        self._access_order.clear()

    def size(self) -> int:
        return len(self._cache)


class EmbeddingService:
    def __init__(self, provider: str = "local", use_cache: bool = True, cache_size: int = 1000):
        self.provider_name = provider
        self.cache = EmbeddingCache(max_size=cache_size) if use_cache else None

        if provider == "openai":
            self.provider = OpenAIEmbeddingProvider()
        elif provider == "local":
            self.provider = LocalEmbeddingProvider()
        else:
            logger.warning(f"Unknown provider: {provider}, using local")
            self.provider = LocalEmbeddingProvider()

        logger.info(f"Embedding service initialized with provider: {self.provider_name}")

    async def embed_text(self, text: str) -> List[float]:
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid text for embedding: {text}")
            return [0.0] * self.provider.get_dimension()

        if self.cache:
            cached = self.cache.get(text)
            if cached is not None:
                return cached

        embedding = await self.provider.embed(text)

        if self.cache:
            self.cache.put(text, embedding)

        return embedding

    async def batch_embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        embeddings = []
        to_embed = []
        to_embed_indices = []

        for i, text in enumerate(texts):
            if self.cache:
                cached = self.cache.get(text)
                if cached is not None:
                    embeddings.append((i, cached))
                else:
                    to_embed.append(text)
                    to_embed_indices.append(i)
            else:
                to_embed.append(text)
                to_embed_indices.append(i)

        if to_embed:
            new_embeddings = await self.provider.batch_embed(to_embed)

            if self.cache:
                for text, embedding in zip(to_embed, new_embeddings):
                    self.cache.put(text, embedding)

            for idx, embedding in zip(to_embed_indices, new_embeddings):
                embeddings.append((idx, embedding))

        embeddings.sort(key=lambda x: x[0])
        return [e[1] for e in embeddings]

    def get_dimension(self) -> int:
        return self.provider.get_dimension()

    def clear_cache(self):
        if self.cache:
            self.cache.clear()

    def get_cache_stats(self) -> dict:
        return {
            "cache_enabled": self.cache is not None,
            "cache_size": self.cache.size() if self.cache else 0,
            "cache_max": self.cache.max_size if self.cache else 0,
            "provider": self.provider_name,
            "dimension": self.provider.get_dimension(),
        }
