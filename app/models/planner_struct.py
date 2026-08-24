from pydantic import BaseModel
from app.workflows.workflow import Workflow
from app.task import Task

class PlannedTask(BaseModel):
    name: str
    executor: str
    depends_on: list[str] = []


class PlannedWorkflow(BaseModel):
    name: str
    tasks: list[PlannedTask]

def to_workflow(plan: PlannedWorkflow) -> Workflow:
    return Workflow(
        name=plan.name,
        tasks=[
            Task(
                name=task.name,
                executor=task.executor,
                depends_on=task.depends_on,
            )
            for task in plan.tasks
        ],
    )
