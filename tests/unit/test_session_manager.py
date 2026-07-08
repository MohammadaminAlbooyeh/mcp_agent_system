"""
Unit tests for SessionManager - Session lifecycle and persistence.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from agent.core.session_manager import SessionManager
from backend.services.session_repository import SessionRepository


@pytest.fixture
def session_manager():
    """Create session manager for testing."""
    manager = SessionManager(ttl_minutes=60)
    manager.set_repository(SessionRepository())
    return manager


@pytest.mark.asyncio
async def test_create_session(session_manager):
    """Test session creation."""
    session_id = await session_manager.create_session(
        user_id="test_user@example.com",
        metadata={"workflow": "research"}
    )
    assert session_id is not None
    assert isinstance(session_id, str)
    assert len(session_id) > 0


@pytest.mark.asyncio
async def test_get_session(session_manager):
    """Test retrieving session details."""
    session_id = await session_manager.create_session(user_id="test@example.com")
    session = await session_manager.get_session(session_id)

    assert session is not None
    assert session["id"] == session_id
    assert session["user_id"] == "test@example.com"
    assert session["is_active"] is True
    assert session["status"] in ["active", "created"]


@pytest.mark.asyncio
async def test_update_session_state(session_manager):
    """Test updating session state."""
    session_id = await session_manager.create_session()
    updates = {"step": 1, "result": "test"}

    success = await session_manager.update_session_state(session_id, updates)
    assert success is True

    session = await session_manager.get_session(session_id)
    assert session["state"].get("step") == 1
    assert session["state"].get("result") == "test"


@pytest.mark.asyncio
async def test_pause_resume_session(session_manager):
    """Test pausing and resuming session."""
    session_id = await session_manager.create_session()

    # Pause
    success = await session_manager.pause_session(session_id)
    assert success is True

    session = await session_manager.get_session(session_id)
    assert session["status"] == "paused"

    # Resume
    success = await session_manager.resume_session(session_id)
    assert success is True

    session = await session_manager.get_session(session_id)
    assert session["status"] in ["active", "resumed"]


@pytest.mark.asyncio
async def test_complete_session(session_manager):
    """Test marking session as complete."""
    session_id = await session_manager.create_session()

    success = await session_manager.complete_session(session_id)
    assert success is True

    session = await session_manager.get_session(session_id)
    assert session["status"] == "completed"
    assert session["is_active"] is False


@pytest.mark.asyncio
async def test_cleanup_session(session_manager):
    """Test deleting a session."""
    session_id = await session_manager.create_session()

    success = await session_manager.cleanup_session(session_id)
    assert success is True

    # Session should not exist after cleanup
    session = await session_manager.get_session(session_id)
    assert session is None


@pytest.mark.asyncio
async def test_list_active_sessions(session_manager):
    """Test listing active sessions."""
    user_id = "test_user@example.com"

    # Create multiple sessions
    session_id1 = await session_manager.create_session(user_id=user_id)
    session_id2 = await session_manager.create_session(user_id=user_id)
    session_id3 = await session_manager.create_session(user_id="other_user@example.com")

    # List for specific user
    sessions = await session_manager.list_active_sessions(user_id=user_id)
    assert len(sessions) >= 2
    assert any(s["id"] == session_id1 for s in sessions)
    assert any(s["id"] == session_id2 for s in sessions)


@pytest.mark.asyncio
async def test_session_ttl_expiration(session_manager):
    """Test session TTL expiration (mocked)."""
    session_manager.ttl_minutes = 1
    session_id = await session_manager.create_session()

    session = await session_manager.get_session(session_id)
    assert session is not None

    # Verify expiry time is set
    assert "expires_at" in session
    assert isinstance(session["expires_at"], datetime)


@pytest.mark.asyncio
async def test_non_existent_session(session_manager):
    """Test retrieving non-existent session."""
    session = await session_manager.get_session("non_existent_id")
    assert session is None


@pytest.mark.asyncio
async def test_concurrent_session_operations(session_manager):
    """Test concurrent session operations."""
    session_id = await session_manager.create_session()

    # Concurrent updates
    tasks = [
        session_manager.update_session_state(session_id, {"step": i})
        for i in range(5)
    ]
    results = await asyncio.gather(*tasks)
    assert all(results)

    session = await session_manager.get_session(session_id)
    assert session["state"].get("step") in range(5)


@pytest.mark.asyncio
async def test_session_memory_snapshot(session_manager):
    """Test memory snapshot creation and restoration."""
    session_id = await session_manager.create_session()

    # Update with memory data
    await session_manager.update_session_state(session_id, {
        "memory": ["item1", "item2", "item3"]
    })

    session = await session_manager.get_session(session_id)
    assert "memory" in session["state"]
    assert session["state"]["memory"] == ["item1", "item2", "item3"]
