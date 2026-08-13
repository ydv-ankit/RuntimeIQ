import uuid
from datetime import datetime, timezone
from enum import Enum

class RunStatus(Enum):
    PENDING = 1
    STARTED = 2
    COMPLETED = 3
    FAILED = 4

class Run:
    def __init__(self, goal: str, status: RunStatus = RunStatus.PENDING, id: str = None , created_at: datetime = None):
        self.id = uuid.UUID(id) if id else uuid.uuid4()
        self.goal = goal
        self.status = status
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc)

    def __repr__(self):
        print("\n==============RUN==============")
        print("id:", self.id)
        print("goal:", self.goal)
        print("status:", self.status)
        print("created_at:", self.created_at)
        print("===============================\n")
