from datetime import datetime
from backend.models.database import Base
from sqlalchemy import Column, String, Text, DateTime, Float, JSON


class ToolCallModel(Base):
    __tablename__ = "tool_calls"

    id = Column(String, primary_key=True)
    execution_id = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    arguments = Column(JSON, default={})
    result = Column(Text)
    error = Column(Text)
    duration_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
