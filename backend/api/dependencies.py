from backend.services.agent_service import AgentService
from backend.services.task_service import TaskService
from backend.services.execution_service import ExecutionService
from backend.services.session_repository import SessionRepository
from agent.core.session_manager import SessionManager

_agent_service = None
_task_service = None
_execution_service = None
_session_manager = None
_session_repository = None


def get_agent_service() -> AgentService:
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service


def get_task_service() -> TaskService:
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service


def get_execution_service() -> ExecutionService:
    global _execution_service
    if _execution_service is None:
        _execution_service = ExecutionService()
    return _execution_service


def get_session_repository() -> SessionRepository:
    global _session_repository
    if _session_repository is None:
        _session_repository = SessionRepository()
    return _session_repository


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        repository = get_session_repository()
        _session_manager = SessionManager(ttl_minutes=1440, enable_persistence=True)
        _session_manager.set_repository(repository)
    return _session_manager
