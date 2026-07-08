"""
Unit tests for Semantic Memory - Embedding and retrieval operations.
"""
import pytest
from agent.memory.memory_manager import MemoryManager


@pytest.fixture
def memory_manager():
    """Create memory manager with local embeddings for testing."""
    return MemoryManager(
        use_semantic=True,
        embedding_provider="local",
        vector_store_type="memory"
    )


@pytest.mark.asyncio
async def test_store_memory(memory_manager):
    """Test storing a memory item."""
    key = "python_async"
    content = "async/await is a pattern for concurrent programming in Python"

    await memory_manager.store(
        content,
        key=key,
        memory_type="long_term"
    )

    # Verify it's in memory
    memory = await memory_manager.retrieve(key, memory_type="long_term")
    assert memory is not None


@pytest.mark.asyncio
async def test_semantic_search(memory_manager):
    """Test semantic similarity search."""
    # Store multiple related items
    items = [
        ("asyncio_docs", "asyncio is a library for writing async code"),
        ("async_patterns", "async/await patterns and best practices"),
        ("concurrency", "concurrent programming with threads and processes"),
        ("javascript_async", "async/await in JavaScript"),
    ]

    for key, content in items:
        await memory_manager.store(content, key=key, memory_type="long_term")

    # Search for async-related content
    results = await memory_manager.semantic_search(
        "python async programming",
        top_k=2
    )

    assert len(results) > 0
    # Should find async-related items
    assert any("async" in str(r).lower() for r in results)


@pytest.mark.asyncio
async def test_hybrid_search(memory_manager):
    """Test hybrid search (keyword + semantic)."""
    items = [
        ("api_design", "REST API design principles and best practices"),
        ("api_patterns", "API patterns and architecture"),
        ("web_services", "Building web services with FastAPI"),
    ]

    for key, content in items:
        await memory_manager.store(content, key=key, memory_type="long_term")

    # Hybrid search
    results = await memory_manager.search(
        "API",
        strategy="hybrid",
        limit=3
    )

    assert len(results) > 0


@pytest.mark.asyncio
async def test_memory_statistics(memory_manager):
    """Test getting memory statistics."""
    # Store some items
    for i in range(5):
        await memory_manager.store(
            f"Item {i} content",
            key=f"item_{i}",
            memory_type="long_term"
        )

    # Get stats
    stats = await memory_manager.get_statistics()

    assert "total_items" in stats or "memory_size" in stats


@pytest.mark.asyncio
async def test_batch_store(memory_manager):
    """Test batch storing multiple items."""
    items = [
        {"key": f"item_{i}", "content": f"Content {i}"}
        for i in range(10)
    ]

    # Batch store
    if hasattr(memory_manager, "batch_store"):
        await memory_manager.batch_store(items)

        # Verify retrieval
        for item in items:
            memory = await memory_manager.retrieve(item["key"], memory_type="long_term")
            assert memory is not None


@pytest.mark.asyncio
async def test_memory_retrieval_strategies(memory_manager):
    """Test different retrieval strategies."""
    items = [
        ("python", "Python programming language"),
        ("python_libs", "Popular Python libraries"),
        ("java", "Java programming language"),
    ]

    for key, content in items:
        await memory_manager.store(content, key=key, memory_type="long_term")

    # Test keyword strategy
    if hasattr(memory_manager, "search"):
        results = await memory_manager.search(
            "python",
            strategy="keyword",
            limit=2
        )
        assert len(results) > 0


@pytest.mark.asyncio
async def test_empty_search(memory_manager):
    """Test search on empty memory."""
    results = await memory_manager.semantic_search("test", top_k=5)
    assert results is not None
    assert len(results) == 0


@pytest.mark.asyncio
async def test_duplicate_keys(memory_manager):
    """Test storing with duplicate keys (should update)."""
    key = "test_key"

    # Store first version
    await memory_manager.store("Version 1", key=key, memory_type="long_term")

    # Store second version (should overwrite)
    await memory_manager.store("Version 2", key=key, memory_type="long_term")

    # Retrieve and verify
    memory = await memory_manager.retrieve(key, memory_type="long_term")
    assert memory is not None


@pytest.mark.asyncio
async def test_special_characters_in_content(memory_manager):
    """Test storing content with special characters."""
    special_content = """
    Special chars: !@#$%^&*()[]{}|;:'",.<>?/\\
    Unicode: 你好世界 مرحبا العالم
    Code: def func(): return x + y
    """

    await memory_manager.store(
        special_content,
        key="special_content",
        memory_type="long_term"
    )

    memory = await memory_manager.retrieve("special_content", memory_type="long_term")
    assert memory is not None
