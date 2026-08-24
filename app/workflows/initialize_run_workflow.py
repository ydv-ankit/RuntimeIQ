from app.repository.workflow_repository import WorkflowRepository
from app.planner import Planner
from app.workflows.validator import WorkflowValidator
from app.workflows.workflow import Workflow
from app.repository.run_repository import RunRepository

class InitializeRunWorkflow:

    def __init__(self, planner, executor_registry):
        self.planner = planner
        self.executor_registry = executor_registry

    async def prepare(self, run) -> Workflow:
        if run.workflow_id:
            return WorkflowRepository.get(run.workflow_id)

        workflow = await self.planner.plan(run.goal.lower())

        is_valid = WorkflowValidator().validate(
            workflow,
            self.executor_registry,
        )
        if not is_valid:
            raise ValueError("Invalid workflow")

        if is_valid:
            workflow_id = WorkflowRepository.create(workflow)

            RunRepository.update_workflow_id(
                run.id,
                workflow_id,
            )

            return workflow