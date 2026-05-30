from datetime import datetime
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MonitoringService:
    def __init__(self):
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tools_called": 0,
            "total_execution_time": 0,
            "started_at": datetime.now(),
        }
        self.events = []

    def record_task_completed(self, duration: float):
        self.metrics["tasks_completed"] += 1
        self.metrics["total_execution_time"] += duration

    def record_task_failed(self):
        self.metrics["tasks_failed"] += 1

    def record_tool_call(self):
        self.metrics["tools_called"] += 1

    def log_event(self, event_type: str, data: dict):
        self.events.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(),
        })

    def get_summary(self) -> dict:
        total = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        return {
            **self.metrics,
            "total_tasks": total,
            "avg_execution_time": (
                self.metrics["total_execution_time"] / self.metrics["tasks_completed"]
                if self.metrics["tasks_completed"] > 0 else 0
            ),
            "uptime": str(datetime.now() - self.metrics["started_at"]),
        }
