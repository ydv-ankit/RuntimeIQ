from app.task import Task

class LogExecutor:
    def execute(self, task: Task):
        return "logs", "user created successfully"