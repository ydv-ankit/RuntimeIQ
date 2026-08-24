from app.workflows.workflow import Workflow
from app.task import Task

class WorkflowParser:

    @staticmethod
    def parse(data: dict) -> Workflow:
        tasks = [
            Task(
                name=task["name"],
                executor=task["executor"],
                depends_on=task.get("depends_on", []),
            )
            for task in data["tasks"]
        ]

        return Workflow(
            name=data["name"],
            tasks=tasks,
        )