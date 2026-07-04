import os
import json
from typing import List, Dict, Optional, Any, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from agent.utils.logger import get_logger
import numpy as np

logger = get_logger(__name__)


@dataclass
class SearchResult:
    id: str
    text: str
    similarity_score: float
    metadata: Dict[str, Any]
    retrieved_at: datetime


class VectorStore(ABC):
    @abstractmethod
    async def store(self, id: str, text: str, embedding: List[float], metadata: dict = None) -> bool:
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass

    @abstractmethod
    async def update(self, id: str, text: str, embedding: List[float], metadata: dict = None) -> bool:
        pass

    @abstractmethod
    async def clear(self) -> bool:
        pass

    @abstractmethod
    def size(self) -> int:
        pass


class FAISSVectorStore(VectorStore):
    def __init__(self, index_path: str = "./data/faiss_index", dimension: int = 384):
        self.index_path = index_path
        self.dimension = dimension
        self.metadata_file = f"{index_path}_metadata.json"

        os.makedirs(os.path.dirname(index_path) if os.path.dirname(index_path) else ".", exist_ok=True)

        self._embeddings = {}
        self._metadata = {}
        self._id_to_idx = {}
        self._idx_counter = 0

        try:
            import faiss
            self.faiss = faiss
            self.index = self._load_index()
        except ImportError:
            logger.warning("FAISS not available, using in-memory fallback")
            self.faiss = None
            self.index = None

        self._load_metadata()

    def _load_index(self):
        if os.path.exists(self.index_path):
            try:
                return self.faiss.read_index(self.index_path)
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")

        index = self.faiss.IndexFlatL2(self.dimension)
        return index

    def _save_index(self):
        if self.index:
            try:
                self.faiss.write_index(self.index, self.index_path)
            except Exception as e:
                logger.error(f"Failed to save FAISS index: {e}")

    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)
                    self._metadata = data.get("metadata", {})
                    self._id_to_idx = data.get("id_to_idx", {})
                    self._idx_counter = data.get("idx_counter", 0)
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")

    def _save_metadata(self):
        try:
            with open(self.metadata_file, "w") as f:
                json.dump({
                    "metadata": self._metadata,
                    "id_to_idx": self._id_to_idx,
                    "idx_counter": self._idx_counter,
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    async def store(self, id: str, text: str, embedding: List[float], metadata: dict = None) -> bool:
        try:
            if id in self._id_to_idx:
                return await self.update(id, text, embedding, metadata)

            if not self.index:
                self._metadata[id] = {"text": text, "metadata": metadata or {}}
                return True

            embedding_array = np.array([embedding], dtype=np.float32)
            self.index.add(embedding_array)

            self._id_to_idx[id] = self._idx_counter
            self._idx_counter += 1
            self._metadata[id] = {"text": text, "metadata": metadata or {}}

            self._save_index()
            self._save_metadata()
            return True
        except Exception as e:
            logger.error(f"Failed to store vector: {e}")
            return False

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        try:
            if not self.index or len(self._metadata) == 0:
                return self._fallback_search(query_embedding, top_k)

            query_array = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_array, min(top_k, len(self._metadata)))

            results = []
            idx_to_id = {v: k for k, v in self._id_to_idx.items()}

            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    continue

                id_str = idx_to_id.get(idx)
                if not id_str or id_str not in self._metadata:
                    continue

                meta = self._metadata[id_str]
                similarity = 1 / (1 + dist)

                results.append(SearchResult(
                    id=id_str,
                    text=meta.get("text", ""),
                    similarity_score=float(similarity),
                    metadata=meta.get("metadata", {}),
                    retrieved_at=datetime.now()
                ))

            return results
        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            return self._fallback_search(query_embedding, top_k)

    def _fallback_search(self, query_embedding: List[float], top_k: int) -> List[SearchResult]:
        query_array = np.array(query_embedding)
        results = []

        similarities = []
        for id_str, meta in self._metadata.items():
            embedding = np.array(meta.get("embedding", []))
            if len(embedding) == 0:
                continue

            similarity = np.dot(query_array, embedding) / (
                np.linalg.norm(query_array) * np.linalg.norm(embedding) + 1e-8
            )
            similarities.append((id_str, similarity, meta))

        similarities.sort(key=lambda x: x[1], reverse=True)

        for id_str, similarity, meta in similarities[:top_k]:
            results.append(SearchResult(
                id=id_str,
                text=meta.get("text", ""),
                similarity_score=float(max(0, similarity)),
                metadata=meta.get("metadata", {}),
                retrieved_at=datetime.now()
            ))

        return results

    async def delete(self, id: str) -> bool:
        try:
            if id in self._metadata:
                del self._metadata[id]
                if id in self._id_to_idx:
                    del self._id_to_idx[id]
                self._save_metadata()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete vector: {e}")
            return False

    async def update(self, id: str, text: str, embedding: List[float], metadata: dict = None) -> bool:
        try:
            await self.delete(id)
            return await self.store(id, text, embedding, metadata)
        except Exception as e:
            logger.error(f"Failed to update vector: {e}")
            return False

    async def clear(self) -> bool:
        try:
            self._metadata.clear()
            self._id_to_idx.clear()
            self._idx_counter = 0

            if self.index:
                import faiss
                self.index = faiss.IndexFlatL2(self.dimension)
                self._save_index()

            self._save_metadata()
            return True
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            return False

    def size(self) -> int:
        return len(self._metadata)

    async def export(self) -> Dict[str, Any]:
        return {
            "size": self.size(),
            "dimension": self.dimension,
            "metadata_count": len(self._metadata),
        }


class InMemoryVectorStore(VectorStore):
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._storage = {}

    async def store(self, id: str, text: str, embedding: List[float], metadata: dict = None) -> bool:
        try:
            self._storage[id] = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {},
                "created_at": datetime.now()
            }
            return True
        except Exception as e:
            logger.error(f"Failed to store vector: {e}")
            return False

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        try:
            if not self._storage:
                return []

            query_array = np.array(query_embedding)
            similarities = []

            for id_str, item in self._storage.items():
                embedding = np.array(item.get("embedding", []))
                if len(embedding) == 0:
                    continue

                similarity = np.dot(query_array, embedding) / (
                    np.linalg.norm(query_array) * np.linalg.norm(embedding) + 1e-8
                )
                similarities.append((id_str, similarity, item))

            similarities.sort(key=lambda x: x[1], reverse=True)

            results = []
            for id_str, similarity, item in similarities[:top_k]:
                results.append(SearchResult(
                    id=id_str,
                    text=item.get("text", ""),
                    similarity_score=float(max(0, similarity)),
                    metadata=item.get("metadata", {}),
                    retrieved_at=datetime.now()
                ))

            return results
        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            return []

    async def delete(self, id: str) -> bool:
        try:
            if id in self._storage:
                del self._storage[id]
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete vector: {e}")
            return False

    async def update(self, id: str, text: str, embedding: List[float], metadata: dict = None) -> bool:
        try:
            await self.delete(id)
            return await self.store(id, text, embedding, metadata)
        except Exception as e:
            logger.error(f"Failed to update vector: {e}")
            return False

    async def clear(self) -> bool:
        try:
            self._storage.clear()
            return True
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            return False

    def size(self) -> int:
        return len(self._storage)
