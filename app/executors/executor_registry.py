from app.executors.metrics import MetricExecutor
from app.executors.database import DatabaseExecutor
from app.executors.logs import LogExecutor
from app.executors.repository import RepositoryExecutor
from app.executors.summary import SummaryExecutor

class ExecutorRegistry:
    def __init__(self):
        self.executors = {}

    def register(self, name, executor):
        self.executors[name] = executor

    def get(self, name):
        executor = self.executors.get(name)

        if executor is None:
            raise ValueError(f"Unknown executor: {name}")

        return executor

    def get_descriptions(self):
        return {
            name: executor.description
            for name, executor in self.executors.items()
        }


registry = ExecutorRegistry()

registry.register("metrics", MetricExecutor())
registry.register("database", DatabaseExecutor())
registry.register("logs", LogExecutor())
registry.register("repository", RepositoryExecutor())
registry.register("summary", SummaryExecutor())