from app.planner import Planner
from app.executors.metrics import MetricExecutor
from app.executors.database import DatabaseExecutor
from app.executors.logs import LogExecutor
from app.executors.repository import RepositoryExecutor
from app.executors.summary import SummaryExecutor
from app.task import Task
import asyncio

class Runtime:
    executorsRegistry = {
        "metrics": MetricExecutor(),
        "database": DatabaseExecutor(),
        "logs": LogExecutor(),
        "repository": RepositoryExecutor(),
        "summary": SummaryExecutor()
    }

    async def run(self, goal: str):
        results = {}
        planner = Planner()
        plan = planner.plan(goal.lower())
        completed_tasks = set()
        remainingTasks: list[Task] = self.get_remaining_tasks(plan, completed_tasks)
        print(remainingTasks)

        execution_context = {}

        # scheduler
        while remainingTasks:
            tasksToExecute = list()
            for task in remainingTasks:
                print("task depends_on", task.name, task.depends_on)
                deps_resolved, deps_context = self.dependencies_resolved(task, completed_tasks, execution_context)
                print("dependencies_resolved:", deps_resolved)
                print("dependencies_context", deps_context)
                if deps_resolved:
                    tasksToExecute.append([task, deps_context])
            if not tasksToExecute:
                raise RuntimeError("No executable tasks remain; possible cyclic dependency")
            
            executions = await asyncio.gather(
                    *(self.execute_task(task, deps_context) for task, deps_context in tasksToExecute)
                )
            print("executions", executions)
            for task, key, value in executions:
                completed_tasks.add(task)
                execution_context[task.name] = {key, value}
                results[task.name] = {key, value}

            remainingTasks = self.get_remaining_tasks(remainingTasks, completed_tasks)

        return results

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
        executor = self.executorsRegistry[task.name]
        key, value = await executor.execute(task.name, deps_context)
        # results[key] = value
        # completed_tasks.add(task)
        # execution_context[task.name] = {key: value}
        return task, key, value