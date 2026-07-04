import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from agent.utils.logger import get_logger
import asyncio
import json

logger = get_logger(__name__)


class SessionManager:
    def __init__(self, ttl_minutes: int = 1440, enable_persistence: bool = True):
        self.ttl_minutes = ttl_minutes
        self.enable_persistence = enable_persistence
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._session_repository = None

    def set_repository(self, repository):
        self._session_repository = repository

    async def create_session(self, user_id: str = None, metadata: dict = None) -> str:
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=self.ttl_minutes)

        session_data = {
            "id": session_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "expires_at": expires_at,
            "state": {},
            "memory_snapshot": {},
            "is_active": True,
            "status": "active",
            "metadata": metadata or {},
            "step_count": 0,
        }

        self._sessions[session_id] = session_data
        self._locks[session_id] = asyncio.Lock()

        if self.enable_persistence and self._session_repository:
            await self._persist_session(session_data)

        logger.info(f"Created session: {session_id} for user: {user_id}")
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if session_id not in self._sessions:
            if self.enable_persistence and self._session_repository:
                return await self._retrieve_session(session_id)
            return None

        session = self._sessions[session_id]
        if self._is_expired(session):
            await self.cleanup_session(session_id)
            return None

        return session

    async def update_session_state(self, session_id: str, state_updates: dict) -> bool:
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return False

        async with self._get_lock(session_id):
            session["state"].update(state_updates)
            session["updated_at"] = datetime.now()

            if self.enable_persistence and self._session_repository:
                await self._persist_session(session)

        return True

    async def save_memory_snapshot(self, session_id: str, memory_state: dict) -> bool:
        session = await self.get_session(session_id)
        if not session:
            return False

        async with self._get_lock(session_id):
            session["memory_snapshot"] = memory_state
            session["updated_at"] = datetime.now()

            if self.enable_persistence and self._session_repository:
                await self._persist_session(session)

        return True

    async def increment_step_count(self, session_id: str) -> int:
        session = await self.get_session(session_id)
        if not session:
            return 0

        async with self._get_lock(session_id):
            session["step_count"] = session.get("step_count", 0) + 1
            session["updated_at"] = datetime.now()

            if self.enable_persistence and self._session_repository:
                await self._persist_session(session)

            return session["step_count"]

    async def pause_session(self, session_id: str) -> bool:
        session = await self.get_session(session_id)
        if not session:
            return False

        async with self._get_lock(session_id):
            session["status"] = "paused"
            session["updated_at"] = datetime.now()

            if self.enable_persistence and self._session_repository:
                await self._persist_session(session)

        logger.info(f"Paused session: {session_id}")
        return True

    async def resume_session(self, session_id: str) -> bool:
        session = await self.get_session(session_id)
        if not session:
            return False

        async with self._get_lock(session_id):
            session["status"] = "active"
            session["updated_at"] = datetime.now()

            if self.enable_persistence and self._session_repository:
                await self._persist_session(session)

        logger.info(f"Resumed session: {session_id}")
        return True

    async def complete_session(self, session_id: str, result: str = None) -> bool:
        session = await self.get_session(session_id)
        if not session:
            return False

        async with self._get_lock(session_id):
            session["status"] = "completed"
            session["is_active"] = False
            session["updated_at"] = datetime.now()
            if result:
                session["metadata"]["final_result"] = result

            if self.enable_persistence and self._session_repository:
                await self._persist_session(session)

        logger.info(f"Completed session: {session_id}")
        return True

    async def cleanup_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
        if session_id in self._locks:
            del self._locks[session_id]

        if self.enable_persistence and self._session_repository:
            await self._delete_session(session_id)

        logger.info(f"Cleaned up session: {session_id}")
        return True

    async def list_active_sessions(self, user_id: str = None, limit: int = 100) -> list:
        active_sessions = []
        for session_id, session in self._sessions.items():
            if not self._is_expired(session) and session["is_active"]:
                if user_id is None or session["user_id"] == user_id:
                    active_sessions.append(session)
                    if len(active_sessions) >= limit:
                        break
        return active_sessions

    async def cleanup_expired_sessions(self) -> int:
        expired_count = 0
        expired_ids = []

        for session_id, session in self._sessions.items():
            if self._is_expired(session):
                expired_ids.append(session_id)
                expired_count += 1

        for session_id in expired_ids:
            await self.cleanup_session(session_id)

        if self.enable_persistence and self._session_repository and expired_ids:
            await self._cleanup_expired_in_db(expired_ids)

        logger.info(f"Cleaned up {expired_count} expired sessions")
        return expired_count

    def _get_lock(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()
        return self._locks[session_id]

    def _is_expired(self, session: dict) -> bool:
        return datetime.now() > session.get("expires_at", datetime.now())

    async def _persist_session(self, session: dict):
        if self._session_repository:
            try:
                await self._session_repository.upsert(session)
            except Exception as e:
                logger.error(f"Failed to persist session {session['id']}: {e}")

    async def _retrieve_session(self, session_id: str) -> Optional[Dict]:
        if self._session_repository:
            try:
                session = await self._session_repository.get_by_id(session_id)
                if session:
                    self._sessions[session_id] = session
                    self._locks[session_id] = asyncio.Lock()
                    return session
            except Exception as e:
                logger.error(f"Failed to retrieve session {session_id}: {e}")
        return None

    async def _delete_session(self, session_id: str):
        if self._session_repository:
            try:
                await self._session_repository.delete(session_id)
            except Exception as e:
                logger.error(f"Failed to delete session {session_id}: {e}")

    async def _cleanup_expired_in_db(self, expired_ids: list):
        if self._session_repository:
            try:
                await self._session_repository.delete_many(expired_ids)
            except Exception as e:
                logger.error(f"Failed to cleanup expired sessions in DB: {e}")
