import json
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from backend.api.schemas import (
    TaskCreate, TaskResponse, AgentRunRequest, AgentRunResponse,
    ToolResponse, ExecutionResponse,
)
from backend.api.dependencies import get_agent_service, get_task_service
from backend.services.agent_service import AgentService
from backend.services.task_service import TaskService
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

_active_connections: dict[str, list[WebSocket]] = {}


async def _broadcast(channel: str, data: dict):
    for ws in _active_connections.get(channel, []):
        try:
            await ws.send_json(data)
        except Exception:
            pass

_settings_store = {
    "llmProvider": "openai",
    "maxSteps": 20,
    "theme": "light",
}


class SettingsUpdate(BaseModel):
    llmProvider: str = "openai"
    maxSteps: int = 20
    theme: str = "light"


@router.post("/agents/run", response_model=AgentRunResponse)
async def run_agent(
    request: AgentRunRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    logger.info(f"API: Run agent with task: {request.task}")
    result = await agent_service.run_task(request.task, request.workflow)
    return AgentRunResponse(task=request.task, result=result, status="completed")


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.create_task(task)


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.list_tasks()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
):
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tools", response_model=list[ToolResponse])
async def list_tools(
    agent_service: AgentService = Depends(get_agent_service),
):
    tools = await agent_service.get_tools()
    return [ToolResponse(name=t.name, description=t.description) for t in tools]


@router.get("/executions", response_model=list[ExecutionResponse])
async def list_executions(
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.list_executions()


@router.get("/settings")
async def get_settings():
    return _settings_store


@router.post("/settings")
async def update_settings(settings: SettingsUpdate):
    _settings_store.update(settings.model_dump())
    logger.info(f"Settings updated: {settings.model_dump()}")
    return _settings_store


@router.get("/monitoring/metrics")
async def get_metrics(
    task_service: TaskService = Depends(get_task_service),
):
    tasks = await task_service.list_tasks()
    executions = await task_service.list_executions()
    completed = len([t for t in tasks if t.get("status") == "completed"])
    failed = len([t for t in tasks if t.get("status") == "failed"])
    tool_calls = len(executions)
    durations = [e.get("duration_ms", 0) for e in executions if e.get("duration_ms")]
    avg_time = sum(durations) / len(durations) if durations else 0
    return {
        "tasks_completed": completed,
        "tasks_failed": failed,
        "tools_called": tool_calls,
        "avg_execution_time": round(avg_time, 3),
    }


@router.websocket("/ws/agent")
async def websocket_agent(websocket: WebSocket):
    await websocket.accept()
    channel = "agent"
    _active_connections.setdefault(channel, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _active_connections[channel].remove(websocket)
        if not _active_connections[channel]:
            del _active_connections[channel]


@router.websocket("/ws/monitoring")
async def websocket_monitoring(websocket: WebSocket):
    await websocket.accept()
    channel = "monitoring"
    _active_connections.setdefault(channel, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _active_connections[channel].remove(websocket)
        if not _active_connections[channel]:
            del _active_connections[channel]
