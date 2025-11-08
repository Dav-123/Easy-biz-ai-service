import uuid
from datetime import datetime
from typing import Dict, Any
from app.modals.schemas import TaskStatus

class TaskService:
    def __init__(self):
        self.active_tasks = {}
    
    def create_task(self) -> str:
        task_id = str(uuid.uuid4())
        self.active_tasks[task_id] = {
            "status": TaskStatus.PENDING,
            "created_at": datetime.utcnow(),
            "result": None,
            "error": None
        }
        return task_id
    
    def update_task(self, task_id: str, status: TaskStatus, result: Dict[str, Any] = None, error: str = None):
        if task_id in self.active_tasks:
            self.active_tasks[task_id].update({
                "status": status,
                "result": result,
                "error": error
            })
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        return self.active_tasks.get(task_id)
