"""
Integration tests for Session Management workflows.
Tests the complete lifecycle of session creation, execution, and completion.
"""
import pytest
from agent.core.session_manager import SessionManager
from backend.services.session_repository import SessionRepository


@pytest.fixture
async def session_setup():
    """Setup session manager and repository."""
    manager = SessionManager(ttl_minutes=60)
    repo = SessionRepository()
    manager.set_repository(repo)
    return manager, repo


@pytest.mark.asyncio
async def test_complete_session_workflow(session_setup):
    """Test complete session lifecycle."""
    session_manager, repo = session_setup
    user_id = "integration_test_user@example.com"

    # Step 1: Create session
    session_id = await session_manager.create_session(
        user_id=user_id,
        metadata={"workflow": "research", "priority": "high"}
    )
    assert session_id is not None

    # Step 2: Verify session created
    session = await session_manager.get_session(session_id)
    assert session["id"] == session_id
    assert session["user_id"] == user_id
    assert session["is_active"] is True

    # Step 3: Update state during execution
    await session_manager.update_session_state(session_id, {
        "step": 1,
        "task": "research python async",
        "tools_used": ["web_search"]
    })

    session = await session_manager.get_session(session_id)
    assert session["state"]["step"] == 1

    # Step 4: Continue with more updates
    await session_manager.update_session_state(session_id, {
        "step": 2,
        "results": ["async is good for IO"],
        "tools_used": ["web_search", "web_scrape"]
    })

    session = await session_manager.get_session(session_id)
    assert session["state"]["step"] == 2

    # Step 5: Pause session
    success = await session_manager.pause_session(session_id)
    assert success is True

    session = await session_manager.get_session(session_id)
    assert session["status"] == "paused"

    # Step 6: Resume session
    success = await session_manager.resume_session(session_id)
    assert success is True

    # Step 7: Final update
    await session_manager.update_session_state(session_id, {
        "step": 3,
        "final_result": "Research complete"
    })

    # Step 8: Complete session
    success = await session_manager.complete_session(session_id)
    assert success is True

    session = await session_manager.get_session(session_id)
    assert session["status"] == "completed"
    assert session["is_active"] is False
    assert session["state"]["final_result"] == "Research complete"


@pytest.mark.asyncio
async def test_multiple_session_isolation(session_setup):
    """Test that multiple sessions don't interfere."""
    session_manager, repo = session_setup

    # Create two sessions
    session_id1 = await session_manager.create_session(user_id="user1@example.com")
    session_id2 = await session_manager.create_session(user_id="user2@example.com")

    # Update with different state
    await session_manager.update_session_state(session_id1, {"data": "session1"})
    await session_manager.update_session_state(session_id2, {"data": "session2"})

    # Verify isolation
    session1 = await session_manager.get_session(session_id1)
    session2 = await session_manager.get_session(session_id2)

    assert session1["state"]["data"] == "session1"
    assert session2["state"]["data"] == "session2"
    assert session1["id"] != session2["id"]


@pytest.mark.asyncio
async def test_session_pause_resume_cycle(session_setup):
    """Test multiple pause/resume cycles."""
    session_manager, repo = session_setup
    session_id = await session_manager.create_session()

    # Multiple pause/resume cycles
    for cycle in range(3):
        await session_manager.update_session_state(session_id, {"cycle": cycle})

        success = await session_manager.pause_session(session_id)
        assert success is True

        session = await session_manager.get_session(session_id)
        assert session["status"] == "paused"
        assert session["state"]["cycle"] == cycle

        success = await session_manager.resume_session(session_id)
        assert success is True

        session = await session_manager.get_session(session_id)
        assert session["status"] in ["active", "resumed"]

    # Final completion
    success = await session_manager.complete_session(session_id)
    assert success is True


@pytest.mark.asyncio
async def test_session_memory_persistence(session_setup):
    """Test that session memory persists across operations."""
    session_manager, repo = session_setup
    session_id = await session_manager.create_session()

    # Store complex memory structure
    memory_data = {
        "research_results": [
            {"url": "https://example.com", "title": "Python Async"},
            {"url": "https://example2.com", "title": "AsyncIO Guide"}
        ],
        "summary": "Found 2 relevant articles",
        "tags": ["async", "python", "concurrency"],
        "step_history": [
            {"step": 1, "action": "search"},
            {"step": 2, "action": "scrape"}
        ]
    }

    await session_manager.update_session_state(session_id, {
        "memory": memory_data,
        "metadata": {"processed": True}
    })

    # Pause and resume
    await session_manager.pause_session(session_id)
    await session_manager.resume_session(session_id)

    # Verify memory persisted
    session = await session_manager.get_session(session_id)
    assert session["state"]["memory"] == memory_data
    assert session["state"]["metadata"]["processed"] is True


@pytest.mark.asyncio
async def test_user_session_filtering(session_setup):
    """Test listing sessions filtered by user."""
    session_manager, repo = session_setup
    user1 = "user1@example.com"
    user2 = "user2@example.com"

    # Create sessions for different users
    user1_sessions = [
        await session_manager.create_session(user_id=user1)
        for _ in range(3)
    ]
    user2_sessions = [
        await session_manager.create_session(user_id=user2)
        for _ in range(2)
    ]

    # List user1 sessions
    listed_sessions = await session_manager.list_active_sessions(user_id=user1)
    user1_ids = {s["id"] for s in listed_sessions}

    # Verify correct filtering
    for session_id in user1_sessions:
        assert session_id in user1_ids

    for session_id in user2_sessions:
        assert session_id not in user1_ids


@pytest.mark.asyncio
async def test_session_cleanup_workflow(session_setup):
    """Test session cleanup and deletion."""
    session_manager, repo = session_setup
    session_ids = [
        await session_manager.create_session()
        for _ in range(5)
    ]

    # Cleanup some sessions
    for session_id in session_ids[:3]:
        success = await session_manager.cleanup_session(session_id)
        assert success is True

    # Verify cleanup
    for session_id in session_ids[:3]:
        session = await session_manager.get_session(session_id)
        assert session is None

    # Others should still exist
    for session_id in session_ids[3:]:
        session = await session_manager.get_session(session_id)
        assert session is not None


@pytest.mark.asyncio
async def test_session_state_accumulation(session_setup):
    """Test that session state accumulates correctly."""
    session_manager, repo = session_setup
    session_id = await session_manager.create_session()

    # First update
    await session_manager.update_session_state(session_id, {
        "step": 1,
        "results": []
    })

    # Second update (should merge/overwrite)
    await session_manager.update_session_state(session_id, {
        "step": 2,
        "results": ["result1"]
    })

    session = await session_manager.get_session(session_id)
    assert session["state"]["step"] == 2
    assert session["state"]["results"] == ["result1"]

    # Third update with additional data
    await session_manager.update_session_state(session_id, {
        "results": ["result1", "result2"],
        "analysis": "complete"
    })

    session = await session_manager.get_session(session_id)
    assert session["state"]["step"] == 2  # Previous step preserved
    assert session["state"]["results"] == ["result1", "result2"]
    assert session["state"]["analysis"] == "complete"
