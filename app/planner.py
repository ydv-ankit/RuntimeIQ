from app.llm.provider import LLMProvider
from app.workflows.workflow import Workflow
from app.models.planner_struct import PlannedWorkflow, to_workflow

class Planner:

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def plan(
        self,
        goal: str,
        executor_descriptions: dict,
    ) -> Workflow:

        prompt = f"""
            You are the workflow planner for RuntimeIQ.

            Convert the user's goal into a minimal executable DAG.

            Available executors:

            {executor_descriptions}

            Rules:

            1. Only use the provided executors.
            2. Every task must have a unique name.
            3. depends_on must reference existing task names.
            4. Tasks without dependencies may execute concurrently.
            5. A task should depend on another task only when it requires
            that task's output.
            6. Do not invent executors.
            7. Do not execute anything.
            8. Keep the workflow as small as possible.

            User goal:

            {goal}
        """

        planned: PlannedWorkflow = await self.llm.generate_structured(
            prompt=prompt,
            response_model=PlannedWorkflow,
        )

        print("PLANNED WORKFLOW")
        print(planned)
        for p in planned.tasks:
            print(p)

        return to_workflow(planned)