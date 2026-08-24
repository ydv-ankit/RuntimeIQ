from app.models.planner_struct import PlannedWorkflow, to_workflow

class Planner:

    def __init__(self, llm):
        self.llm = llm

    async def plan(self, goal, executor_registry):
        executor_descriptions = (
            executor_registry.get_descriptions()
        )

        prompt = self.build_prompt(
            goal,
            executor_descriptions,
        )

        plan = await self.llm.generate_structured(
            prompt,
            PlannedWorkflow,
        )

        return to_workflow(plan)

    def build_prompt(self, goal, descriptions):
        return """
        You are the workflow planner for RuntimeIQ.

        Your job is to convert a user's goal into an executable DAG.

        Available executors:

        {executors}

        Rules:

        1. Only use executors from the provided list.
        2. Every task must have a unique name.
        3. depends_on must reference existing task names.
        4. Tasks with no dependency may execute concurrently.
        5. A task should depend on another task only when it needs its output.
        6. Do not perform execution yourself.
        7. Do not invent executors.
        8. Keep the workflow as small as possible while satisfying the goal.

        User goal:

        {goal}
        """