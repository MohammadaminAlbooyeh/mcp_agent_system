from datetime import datetime
from backend.models.database import Base
from sqlalchemy import Column, String, Text, DateTime, Float, JSON


class ExecutionModel(Base):
    __tablename__ = "executions"

    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    params = Column(JSON, default={})
    result = Column(Text)
    status = Column(String, default="pending")
    duration_ms = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.now)
