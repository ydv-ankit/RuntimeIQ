class WorkflowValidator:

    def validate(self, workflow, executor_registry):
        self.validate_unique_tasks(workflow)
        self.validate_dependencies(workflow)
        self.validate_executors(workflow, executor_registry)
        self.validate_no_cycles(workflow)

    def validate_unique_tasks(self, workflow):
        task_names = [task.name for task in workflow.tasks]

        if len(task_names) != len(set(task_names)):
            raise ValueError(
                "Workflow contains duplicate task names"
            )

    def validate_dependencies(self, workflow):
        task_names = {task.name for task in workflow.tasks}

        for task in workflow.tasks:
            for dependency in task.depends_on:
                if dependency not in task_names:
                    raise ValueError(
                        f"Task '{task.name}' depends on "
                        f"unknown task '{dependency}'"
                    )

    def validate_executors(self, workflow, executor_registry):
        for task in workflow.tasks:
            try:
                executor_registry.get(task.executor)
            except ValueError:
                raise ValueError(
                    f"Unknown executor '{task.executor}' "
                    f"for task '{task.name}'"
                )

    def validate_no_cycles(self, workflow):
        graph = {
            task.name: task.depends_on
            for task in workflow.tasks
        }

        state = {}

        def visit(task_name):
            current_state = state.get(task_name, 0)

            if current_state == 1:
                raise ValueError(
                    f"Cycle detected involving task '{task_name}'"
                )

            if current_state == 2:
                return

            state[task_name] = 1

            for dependency in graph[task_name]:
                visit(dependency)

            state[task_name] = 2

        for task in workflow.tasks:
            visit(task.name)