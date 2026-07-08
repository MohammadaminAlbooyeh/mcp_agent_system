"""
Load tests for concurrent session operations.
Tests system performance and stability under concurrent load.
"""
import pytest
import asyncio
import time
from agent.core.session_manager import SessionManager
from backend.services.session_repository import SessionRepository


@pytest.fixture
async def session_manager_for_load():
    """Create session manager for load testing."""
    manager = SessionManager(ttl_minutes=60)
    manager.set_repository(SessionRepository())
    return manager


@pytest.mark.asyncio
async def test_concurrent_session_creation(session_manager_for_load):
    """Test creating multiple sessions concurrently."""
    num_sessions = 50
    start_time = time.time()

    tasks = [
        session_manager_for_load.create_session(user_id=f"user_{i}@example.com")
        for i in range(num_sessions)
    ]
    session_ids = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time
    throughput = num_sessions / elapsed

    assert len(session_ids) == num_sessions
    assert all(isinstance(sid, str) for sid in session_ids)
    assert len(set(session_ids)) == num_sessions  # All unique

    print(f"\nSession Creation Throughput: {throughput:.0f} sessions/second")
    print(f"Time: {elapsed:.2f}s for {num_sessions} sessions")

    # Performance threshold: should complete in reasonable time
    assert elapsed < 30  # 50 sessions in less than 30 seconds


@pytest.mark.asyncio
async def test_concurrent_state_updates(session_manager_for_load):
    """Test concurrent state updates on same session."""
    session_id = await session_manager_for_load.create_session()
    num_updates = 100

    start_time = time.time()

    tasks = [
        session_manager_for_load.update_session_state(
            session_id,
            {"update": i, "data": f"data_{i}"}
        )
        for i in range(num_updates)
    ]
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time
    throughput = num_updates / elapsed

    assert all(results)
    print(f"\nState Update Throughput: {throughput:.0f} updates/second")
    print(f"Time: {elapsed:.2f}s for {num_updates} updates")


@pytest.mark.asyncio
async def test_concurrent_session_retrieval(session_manager_for_load):
    """Test retrieving many sessions concurrently."""
    # Create multiple sessions first
    num_sessions = 30
    session_ids = [
        await session_manager_for_load.create_session(user_id=f"user_{i}@example.com")
        for i in range(num_sessions)
    ]

    start_time = time.time()

    # Retrieve all concurrently
    tasks = [
        session_manager_for_load.get_session(sid)
        for sid in session_ids
    ]
    sessions = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time
    throughput = num_sessions / elapsed

    assert len(sessions) == num_sessions
    assert all(s is not None for s in sessions)

    print(f"\nSession Retrieval Throughput: {throughput:.0f} retrievals/second")
    print(f"Time: {elapsed:.2f}s for {num_sessions} retrievals")


@pytest.mark.asyncio
async def test_mixed_concurrent_operations(session_manager_for_load):
    """Test mixed create/update/retrieve operations concurrently."""
    operations = []
    num_ops = 100

    start_time = time.time()

    # Create some sessions
    create_tasks = [
        session_manager_for_load.create_session(user_id=f"user_{i}@example.com")
        for i in range(20)
    ]
    session_ids = await asyncio.gather(*create_tasks)

    # Mix of operations on created sessions
    mixed_tasks = []
    for i in range(80):
        session_idx = i % len(session_ids)
        session_id = session_ids[session_idx]

        if i % 3 == 0:
            task = session_manager_for_load.get_session(session_id)
        elif i % 3 == 1:
            task = session_manager_for_load.update_session_state(
                session_id,
                {"operation": i}
            )
        else:
            task = session_manager_for_load.list_active_sessions(limit=10)

        mixed_tasks.append(task)

    results = await asyncio.gather(*mixed_tasks)
    elapsed = time.time() - start_time

    print(f"\nMixed Operations Throughput: {num_ops / elapsed:.0f} ops/second")
    print(f"Time: {elapsed:.2f}s for {num_ops} mixed operations")


@pytest.mark.asyncio
async def test_session_stress_with_state(session_manager_for_load):
    """Stress test with large state objects."""
    num_sessions = 20

    session_ids = [
        await session_manager_for_load.create_session()
        for _ in range(num_sessions)
    ]

    # Create large state objects
    large_state = {
        "data": ["item_" + str(i) for i in range(1000)],
        "metadata": {
            "nested": {
                "deeply": {
                    "value": "test" * 100
                }
            }
        },
        "results": [{"id": i, "value": f"result_{i}"} for i in range(100)]
    }

    start_time = time.time()

    tasks = [
        session_manager_for_load.update_session_state(sid, large_state)
        for sid in session_ids
    ]
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time

    assert all(results)
    print(f"\nLarge State Update: {elapsed:.2f}s for {num_sessions} large updates")


@pytest.mark.asyncio
async def test_pause_resume_concurrent(session_manager_for_load):
    """Test concurrent pause/resume operations."""
    num_sessions = 30
    session_ids = [
        await session_manager_for_load.create_session()
        for _ in range(num_sessions)
    ]

    start_time = time.time()

    # Concurrent pause
    pause_tasks = [
        session_manager_for_load.pause_session(sid)
        for sid in session_ids
    ]
    pause_results = await asyncio.gather(*pause_tasks)

    pause_time = time.time()

    # Concurrent resume
    resume_tasks = [
        session_manager_for_load.resume_session(sid)
        for sid in session_ids
    ]
    resume_results = await asyncio.gather(*resume_tasks)

    total_time = time.time() - start_time

    assert all(pause_results)
    assert all(resume_results)

    print(f"\nPause: {pause_time - start_time:.2f}s for {num_sessions} operations")
    print(f"Resume: {total_time - pause_time:.2f}s for {num_sessions} operations")
    print(f"Total: {total_time:.2f}s")


@pytest.mark.asyncio
async def test_cleanup_performance(session_manager_for_load):
    """Test cleanup performance with multiple sessions."""
    num_sessions = 100

    session_ids = [
        await session_manager_for_load.create_session()
        for _ in range(num_sessions)
    ]

    start_time = time.time()

    # Concurrent cleanup
    cleanup_tasks = [
        session_manager_for_load.cleanup_session(sid)
        for sid in session_ids
    ]
    results = await asyncio.gather(*cleanup_tasks)

    elapsed = time.time() - start_time
    throughput = num_sessions / elapsed

    assert all(results)
    print(f"\nCleanup Throughput: {throughput:.0f} sessions/second")
    print(f"Time: {elapsed:.2f}s for {num_sessions} cleanups")


@pytest.mark.asyncio
async def test_session_lifecycle_under_load(session_manager_for_load):
    """Test complete session lifecycle under load."""
    async def full_session_lifecycle(user_id, session_num):
        """Execute full session lifecycle."""
        # Create
        session_id = await session_manager_for_load.create_session(user_id=user_id)

        # Update state multiple times
        for step in range(5):
            await session_manager_for_load.update_session_state(
                session_id,
                {"step": step, "progress": step * 20}
            )

        # Pause
        await session_manager_for_load.pause_session(session_id)

        # Resume
        await session_manager_for_load.resume_session(session_id)

        # Final update
        await session_manager_for_load.update_session_state(
            session_id,
            {"complete": True}
        )

        # Complete
        await session_manager_for_load.complete_session(session_id)

        return True

    num_sessions = 10
    start_time = time.time()

    tasks = [
        full_session_lifecycle(f"user_{i}@example.com", i)
        for i in range(num_sessions)
    ]
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time

    assert all(results)
    print(f"\nFull Lifecycle Throughput: {num_sessions / elapsed:.1f} sessions/second")
    print(f"Time: {elapsed:.2f}s for {num_sessions} complete lifecycles")
    print(f"Average per session: {elapsed / num_sessions:.2f}s")
