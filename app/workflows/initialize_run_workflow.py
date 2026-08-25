from app.repository.workflow_repository import WorkflowRepository
from app.planner import Planner
from app.workflows.validator import WorkflowValidator
from app.workflows.workflow import Workflow
from app.repository.run_repository import RunRepository
from app.config.logging import logger

class InitializeRunWorkflow:

    def __init__(self, planner: Planner, executor_registry):
        self.planner = planner
        self.executor_registry = executor_registry

    async def prepare(self, run) -> Workflow:
        try:
            if run.workflow_id:
                return WorkflowRepository.get(run.workflow_id)

            workflow = await self.planner.plan(
                run.goal,
                self.executor_registry.get_descriptions(),
            )

            print("WORKFLOW CREATED")

            WorkflowValidator().validate(
                workflow,
                self.executor_registry,
            )
            workflow_id = WorkflowRepository.create(workflow)

            RunRepository.update_workflow_id(
                run.id,
                workflow_id,
            )

            return workflow
        except Exception:
            logger.error("failed to create workflow")
            raise