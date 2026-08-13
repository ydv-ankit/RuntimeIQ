from app.planner import Planner
from app.executors.metrics import MetricExecutor
from app.executors.database import DatabaseExecutor
from app.executors.logs import LogExecutor
from app.executors.repository import RepositoryExecutor
from app.executors.summary import SummaryExecutor
from app.models.run import Run, RunStatus
from app.task import Task
from app.repository.run_repository import RunRepository
import asyncio

class Runtime:
    executorsRegistry = {
        "metrics": MetricExecutor(),
        "database": DatabaseExecutor(),
        "logs": LogExecutor(),
        "repository": RepositoryExecutor(),
        "summary": SummaryExecutor()
    }

    async def execute(self, run: Run):
        results = {
            "COMPLETED": {},
            "FAILED": []
        }
        run.status = RunStatus.RUNNING
        RunRepository.update_status(run.id, run.status)
        planner = Planner()
        plan = planner.plan(run.goal.lower())
        completed_tasks = set()
        remaining_tasks: list[Task] = self.get_remaining_tasks(plan, completed_tasks)
        print(remaining_tasks)

        execution_context = {}

        # scheduler
        workflow_failed = False
        while remaining_tasks and not workflow_failed:
            tasks_to_execute = list()
            for task in remaining_tasks:
                print("task depends_on", task.name, task.depends_on)
                deps_resolved, deps_context = self.dependencies_resolved(task, completed_tasks, execution_context)
                print("dependencies_resolved:", deps_resolved)
                print("dependencies_context", deps_context)
                if deps_resolved:
                    tasks_to_execute.append([task, deps_context])
            if not tasks_to_execute:
                raise RuntimeError("No executable tasks remain; possible cyclic dependency")
            
            executions = await asyncio.gather(
                    *(self.execute_task(task, deps_context) for task, deps_context in tasks_to_execute),
                    return_exceptions=True
                )
            print("executions", executions)
            for task, execution in executions:
                print(task, execution)
                if isinstance(execution, Exception):
                    workflow_failed = True
                    print("Task failed:", execution)
                    results["FAILED"].append({task.name: str(execution)})
                    continue
                completed_tasks.add(task)
                execution_context[task.name] = execution
                results["COMPLETED"][task.name] = execution


            remaining_tasks = self.get_remaining_tasks(remaining_tasks, completed_tasks)

        if workflow_failed:
            run.status = RunStatus.FAILED
        else:
            run.status = RunStatus.COMPLETED
        RunRepository.update_status(run.id, run.status)
        return results, workflow_failed

    def dependencies_resolved(self, task, completed_tasks, execution_context):
        dependencies_resolved = True
        context = dict()
        for dep in task.depends_on:
            if dep not in completed_tasks:
                dependencies_resolved = False
                break
            print(dep.name)
            context[dep.name] = execution_context[dep.name]
        return dependencies_resolved, context

    def get_remaining_tasks(self, tasksList, completed_tasks):
        remainingTasks = []
        for task in tasksList:
            if task not in completed_tasks:
                remainingTasks.append(task)
        return remainingTasks

    async def execute_task(self, task: Task, deps_context: dict):
        try:
            executor = self.executorsRegistry[task.name]
            key, value = await executor.execute(task.name, deps_context)
            return task, {key: value}
        except Exception as e:
            return task, e