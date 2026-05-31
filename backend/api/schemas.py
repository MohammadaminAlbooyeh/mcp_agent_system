from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AgentRunRequest(BaseModel):
    task: str
    workflow: Optional[str] = None


class AgentRunResponse(BaseModel):
    task: str
    result: str
    status: str


class ToolResponse(BaseModel):
    name: str
    description: str


class ExecutionResponse(BaseModel):
    id: str
    task_id: str
    tool_name: str
    params: dict
    result: str
    status: str
    duration_ms: float
    timestamp: datetime
