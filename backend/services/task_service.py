from datetime import datetime
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class TaskService:
    def __init__(self):
        self._tasks = {}
        self._executions = []

    async def create_task(self, task_data) -> dict:
        task = {
            "id": f"task_{len(self._tasks) + 1}",
            "title": task_data.title,
            "description": task_data.description,
            "priority": task_data.priority,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": None,
        }
        self._tasks[task["id"]] = task
        logger.info(f"Created task: {task['id']}")
        return task

    async def list_tasks(self) -> list[dict]:
        return list(self._tasks.values())

    async def get_task(self, task_id: str) -> dict:
        return self._tasks.get(task_id)

    async def list_executions(self) -> list[dict]:
        return self._executions

    async def log_execution(self, execution: dict):
        self._executions.append(execution)
