
from datetime import datetime
from backend.models.database import get_session, close_session
from backend.models.task import TaskModel
from backend.models.execution import ExecutionModel
from backend.utils.helpers import generate_id
from backend.utils.redis_client import get_redis_client
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class TaskService:
    async def create_task(self, task_data) -> dict:
        redis = get_redis_client()
        cache_key = f"task:{task_data.title}"
        if redis.exists(cache_key):
            return redis.get(cache_key)
        session = get_session()
        try:
            task = TaskModel(
                id=generate_id("task_"),
                title=task_data.title,
                description=task_data.description,
                priority=task_data.priority,
                status="pending",
                created_at=datetime.now(),
            )
            session.add(task)
            session.commit()
            result = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "status": task.status,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
            }
            redis.set(cache_key, str(result))
            logger.info(f"Created task: {task.id}")
            return result
        finally:
            close_session(session)

    async def list_tasks(self) -> list:
        redis = get_redis_client()
        cache_key = "tasks:list"
        cached = redis.get(cache_key)
        if cached:
            import json
            try:
                return json.loads(cached)
            except Exception:
                pass
        session = get_session()
        try:
            tasks = session.query(TaskModel).all()
            result = [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "status": t.status,
                    "created_at": t.created_at,
                    "updated_at": t.updated_at,
                }
                for t in tasks
            ]
            redis.set(cache_key, str(result))
            return result
        finally:
            close_session(session)

    async def get_task(self, task_id: str) -> dict:
        redis = get_redis_client()
        cache_key = f"task:{task_id}"
        cached = redis.get(cache_key)
        if cached:
            import json
            try:
                return json.loads(cached)
            except Exception:
                pass
        session = get_session()
        try:
            task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if not task:
                return None
            result = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "status": task.status,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
            }
            redis.set(cache_key, str(result))
            return result
        finally:
            close_session(session)

    async def list_executions(self) -> list[dict]:
        session = get_session()
        try:
            executions = session.query(ExecutionModel).all()
            return [
                {
                    "id": e.id,
                    "task_id": e.task_id,
                    "tool_name": e.tool_name,
                    "params": e.params or {},
                    "result": e.result,
                    "status": e.status,
                    "duration_ms": e.duration_ms,
                    "timestamp": e.timestamp,
                }
                for e in executions
            ]
        finally:
            close_session(session)

    async def log_execution(self, execution: dict):
        session = get_session()
        try:
            exec_entry = ExecutionModel(
                id=execution.get("id", generate_id("exec_")),
                task_id=execution.get("task_id", ""),
                tool_name=execution.get("tool_name", ""),
                params=execution.get("params", {}),
                result=execution.get("result", ""),
                status=execution.get("status", "completed"),
                duration_ms=execution.get("duration_ms", 0.0),
                timestamp=datetime.now(),
            )
            session.add(exec_entry)
            session.commit()
            self._invalidate_cache()
        finally:
            close_session(session)

    def _invalidate_cache(self):
        redis = get_redis_client()
        redis.delete("tasks:list")
