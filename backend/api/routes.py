import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from backend.api.schemas import (
    TaskCreate, TaskResponse, AgentRunRequest, AgentRunResponse,
    ToolResponse, ExecutionResponse,
)
from backend.api.dependencies import get_agent_service, get_task_service
from backend.services.agent_service import AgentService
from backend.services.task_service import TaskService
from backend.utils.helpers import generate_id
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


@router.post("/agents/run", response_model=AgentRunResponse, tags=["Agents"])
async def run_agent(
    request: AgentRunRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Execute an agent task with optional workflow specification.

    This endpoint runs the AI agent with the provided task and returns the result
    after the agent completes execution using ReAct reasoning pattern.

    Args:
        request (AgentRunRequest): Contains task description and optional workflow name

    Returns:
        AgentRunResponse: Contains the task, result, and completion status

    Example:
        ```json
        {
            "task": "Search for Python async best practices and summarize top 5",
            "workflow": null
        }
        ```
    """
    logger.info(f"API: Run agent with task: {request.task}")
    result = await agent_service.run_task(request.task, request.workflow)
    return AgentRunResponse(task=request.task, result=result, status="completed")


@router.post("/tasks", response_model=TaskResponse, tags=["Tasks"])
async def create_task(
    task: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
):
    """
    Create a new task for the agent to execute.

    Args:
        task (TaskCreate): Task title, description, and priority level

    Returns:
        TaskResponse: Created task with ID, timestamps, and status

    Example:
        ```json
        {
            "title": "Research Python async",
            "description": "Find and summarize async patterns",
            "priority": "high"
        }
        ```
    """
    return await task_service.create_task(task)


@router.get("/tasks", response_model=list[TaskResponse], tags=["Tasks"])
async def list_tasks(
    task_service: TaskService = Depends(get_task_service),
):
    """
    Retrieve all tasks with their current status and details.

    Returns:
        list[TaskResponse]: List of all tasks including created, in-progress, and completed
    """
    return await task_service.list_tasks()


@router.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
):
    """
    Get a specific task by ID.

    Args:
        task_id (str): Unique task identifier

    Returns:
        TaskResponse: Task details including state and execution info

    Raises:
        HTTPException: 404 if task not found
    """
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tools", response_model=list[ToolResponse], tags=["Tools"])
async def list_tools(
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Get list of all available MCP tools the agent can use.

    Returns:
        list[ToolResponse]: Available tools with names and descriptions.
        Includes: web_search, database_query, file_read, file_write, email_send,
        http_request, code_execute, web_scrape, and utility tools
    """
    tools = await agent_service.get_tools()
    return [ToolResponse(name=t.name, description=t.description) for t in tools]


@router.post("/executions/execute", response_model=ExecutionResponse, tags=["Execution"])
async def execute_tool(
    request: dict,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Execute a specific MCP tool with provided parameters.

    This endpoint allows direct execution of any available tool from the MCP server,
    useful for testing and direct tool invocation without agent reasoning.

    Args:
        request (dict): Contains:
            - name (str): Tool name (required)
            - params (dict): Tool-specific parameters (optional)

    Returns:
        ExecutionResponse: Execution result, status, duration, and timestamp

    Example:
        ```json
        {
            "name": "web_search",
            "params": {
                "query": "python async",
                "num_results": 5
            }
        }
        ```

    Raises:
        HTTPException: 400 if tool name missing, 404 if tool not found
    """
    tool_name = request.get("name")
    params = request.get("params", {})
    if not tool_name:
        raise HTTPException(status_code=400, detail="Tool name is required")
    import time
    start = time.time()
    try:
        tools = await agent_service.get_tools()
        tool_map = {t.name: t for t in tools}
        tool = tool_map.get(tool_name)
        if tool is None:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        result = await tool.execute(**params)
        status = "success"
    except HTTPException:
        raise
    except Exception as e:
        result = str(e)
        status = "failed"
    elapsed = (time.time() - start) * 1000
    return ExecutionResponse(
        id=f"exec_{datetime.now().timestamp()}",
        task_id="direct_execution",
        tool_name=tool_name,
        params=params,
        result=str(result),
        status=status,
        duration_ms=elapsed,
        timestamp=datetime.now(),
    )


@router.get("/executions", response_model=list[ExecutionResponse], tags=["Execution"])
async def list_executions(
    task_service: TaskService = Depends(get_task_service),
):
    """
    Get history of all tool executions.

    Returns:
        list[ExecutionResponse]: List of all tool executions with results and timing
    """
    return await task_service.list_executions()


@router.get("/settings", tags=["Configuration"])
async def get_settings():
    """
    Get current system settings and configuration.

    Returns:
        dict: Current settings including LLM provider, max steps, and theme
    """
    return _settings_store


@router.post("/settings", tags=["Configuration"])
async def update_settings(settings: SettingsUpdate):
    """
    Update system settings and configuration.

    Args:
        settings (SettingsUpdate): New settings for LLM provider, max steps, theme

    Returns:
        dict: Updated settings

    Example:
        ```json
        {
            "llmProvider": "claude",
            "maxSteps": 25,
            "theme": "dark"
        }
        ```
    """
    _settings_store.update(settings.model_dump())
    logger.info(f"Settings updated: {settings.model_dump()}")
    return _settings_store


@router.get("/monitoring/metrics", tags=["Monitoring"])
async def get_metrics(
    task_service: TaskService = Depends(get_task_service),
):
    """
    Get system metrics and performance statistics.

    Returns performance data including:
    - Task completion and failure counts
    - Total tool invocations
    - Average execution time across all operations

    Returns:
        dict: Metrics including tasks_completed, tasks_failed, tools_called, avg_execution_time
    """
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
    """
    WebSocket endpoint for real-time agent execution updates.

    Provides real-time streaming of:
    - Agent reasoning steps
    - Tool invocations and results
    - Task progress and status updates
    - Error notifications

    Connect: ws://localhost:8000/api/ws/agent
    """
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
    """
    WebSocket endpoint for real-time system monitoring.

    Provides real-time streaming of:
    - System metrics (CPU, memory, disk)
    - API latency and throughput
    - Tool execution metrics
    - Error rates and patterns

    Connect: ws://localhost:8000/api/ws/monitoring
    """
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
