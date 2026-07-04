from datetime import datetime
from backend.models.database import Base
from sqlalchemy import Column, String, DateTime, Boolean, JSON
import uuid


class OAuthTokenModel(Base):
    __tablename__ = "oauth_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    provider = Column(String, nullable=False)  # gmail, outlook, etc
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    scopes = Column(JSON, default=[])
    user_email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def is_expired(self) -> bool:
        if not self.token_expiry:
            return False
        return datetime.now() > self.token_expiry

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "provider": self.provider,
            "user_email": self.user_email,
            "is_active": self.is_active,
            "is_expired": self.is_expired(),
            "token_expiry": self.token_expiry.isoformat() if self.token_expiry else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
