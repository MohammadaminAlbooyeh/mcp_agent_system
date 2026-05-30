from datetime import datetime
from backend.models.database import Base
from sqlalchemy import Column, String, Text, DateTime, JSON


class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    llm_provider = Column(String, default="openai")
    config = Column(JSON, default={})
    status = Column(String, default="idle")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
