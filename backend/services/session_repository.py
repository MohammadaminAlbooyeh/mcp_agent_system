from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.models.session import SessionModel
from backend.models.database import SessionLocal, get_session
from agent.utils.logger import get_logger
import asyncio

logger = get_logger(__name__)


class SessionRepository:
    def __init__(self):
        self.db = None

    async def create(self, session_data: Dict[str, Any]) -> SessionModel:
        db = get_session()
        try:
            session = SessionModel(
                id=session_data.get("id"),
                user_id=session_data.get("user_id"),
                state=session_data.get("state", {}),
                memory_snapshot=session_data.get("memory_snapshot", {}),
                expires_at=session_data.get("expires_at"),
                is_active=session_data.get("is_active", True),
                status=session_data.get("status", "active"),
                metadata=session_data.get("metadata", {}),
            )
            session.step_count = session_data.get("step_count", 0)
            db.add(session)
            db.commit()
            db.refresh(session)
            logger.info(f"Created session in DB: {session.id}")
            return session
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create session: {e}")
            raise
        finally:
            db.close()

    async def get_by_id(self, session_id: str) -> Optional[SessionModel]:
        db = get_session()
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            return session
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
        finally:
            db.close()

    async def update(self, session_id: str, updates: Dict[str, Any]) -> bool:
        db = get_session()
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if not session:
                return False

            for key, value in updates.items():
                if hasattr(session, key):
                    setattr(session, key, value)

            session.updated_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update session {session_id}: {e}")
            return False
        finally:
            db.close()

    async def upsert(self, session_data: Dict[str, Any]) -> SessionModel:
        db = get_session()
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_data.get("id")).first()

            if session:
                session.state = session_data.get("state", {})
                session.memory_snapshot = session_data.get("memory_snapshot", {})
                session.status = session_data.get("status", session.status)
                session.is_active = session_data.get("is_active", session.is_active)
                session.session_metadata = session_data.get("metadata", {})
                session.step_count = session_data.get("step_count", session.step_count)
                session.updated_at = datetime.now()
            else:
                session = SessionModel(
                    id=session_data.get("id"),
                    user_id=session_data.get("user_id"),
                    state=session_data.get("state", {}),
                    memory_snapshot=session_data.get("memory_snapshot", {}),
                    expires_at=session_data.get("expires_at"),
                    is_active=session_data.get("is_active", True),
                    status=session_data.get("status", "active"),
                    metadata=session_data.get("metadata", {}),
                )
                session.step_count = session_data.get("step_count", 0)
                db.add(session)

            db.commit()
            db.refresh(session)
            return session
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to upsert session: {e}")
            raise
        finally:
            db.close()

    async def delete(self, session_id: str) -> bool:
        db = get_session()
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if session:
                db.delete(session)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
        finally:
            db.close()

    async def delete_many(self, session_ids: List[str]) -> int:
        db = get_session()
        try:
            count = db.query(SessionModel).filter(SessionModel.id.in_(session_ids)).delete()
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete sessions: {e}")
            return 0
        finally:
            db.close()

    async def list_active(self, user_id: str = None, limit: int = 100) -> List[SessionModel]:
        db = get_session()
        try:
            query = db.query(SessionModel).filter(
                SessionModel.is_active == True,
                SessionModel.expires_at > datetime.now()
            )

            if user_id:
                query = query.filter(SessionModel.user_id == user_id)

            return query.limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to list active sessions: {e}")
            return []
        finally:
            db.close()

    async def get_by_user_id(self, user_id: str, limit: int = 100) -> List[SessionModel]:
        db = get_session()
        try:
            return db.query(SessionModel).filter(
                SessionModel.user_id == user_id
            ).order_by(SessionModel.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []
        finally:
            db.close()

    async def cleanup_expired(self) -> int:
        db = get_session()
        try:
            count = db.query(SessionModel).filter(
                SessionModel.expires_at <= datetime.now()
            ).delete()
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0
        finally:
            db.close()
