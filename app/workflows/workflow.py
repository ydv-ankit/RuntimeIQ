from app.task import Task

class Workflow:
    name: str
    tasks: list[Task]

    def __init__(self, name: str, tasks: list[Task]):
        self.name = name
        self.tasks = tasks