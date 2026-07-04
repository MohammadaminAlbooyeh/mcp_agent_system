from datetime import datetime, timedelta
from backend.models.database import Base
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer
import uuid


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    state = Column(JSON, default={})
    memory_snapshot = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    status = Column(String, default="active")  # active, paused, completed, expired, terminated
    session_metadata = Column(JSON, default={})
    step_count = Column(Integer, default=0)

    def __init__(self, user_id=None, ttl_minutes=1440, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
        self.is_active = True
        self.status = "active"

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "state": self.state or {},
            "memory_snapshot": self.memory_snapshot or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "status": self.status,
            "metadata": self.session_metadata or {},
            "step_count": self.step_count,
        }
