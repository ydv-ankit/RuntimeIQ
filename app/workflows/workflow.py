from app.task import Task
from datetime import datetime

class Workflow:
    id: str | None
    name: str
    tasks: list[Task]
    created_at: datetime | None

    def __init__(
        self,
        name: str,
        tasks: list[Task],
        id: str | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.name = name
        self.tasks = tasks
        self.created_at = created_at