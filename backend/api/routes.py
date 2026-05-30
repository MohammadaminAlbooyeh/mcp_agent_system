from fastapi import APIRouter, Depends, HTTPException
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


@router.get("/monitoring/metrics")
async def get_metrics():
    return {
        "tasks_completed": 0,
        "tasks_failed": 0,
        "tools_called": 0,
        "avg_execution_time": 0,
    }
