from app.planner import Planner
from app.executors.metrics import MetricExecutor
from app.executors.database import DatabaseExecutor
from app.executors.logs import LogExecutor
from app.executors.repository import RepositoryExecutor
from app.executors.summary import SummaryExecutor
from app.task import Task

class Runtime:
    executorsRegistry = {
        "metrics": MetricExecutor(),
        "database": DatabaseExecutor(),
        "logs": LogExecutor(),
        "repository": RepositoryExecutor(),
        "summary": SummaryExecutor()
    }

    def run(self, goal: str):
        results = {}
        planner = Planner()
        plan = planner.plan(goal.lower())
        completed_tasks = set()
        remainingTasks: list[Task] = self.getRemainingTasks(plan, completed_tasks)
        print(remainingTasks)

        # scheduler
        while remainingTasks:
            for task in remainingTasks:
                print("task depends_on", task.name, task.depends_on)
                dependencies_resolved = self.dependenciesResolved(task, completed_tasks)
                print("dependencies_resolved:", dependencies_resolved)
                executor = self.executorsRegistry[task.name]
                if dependencies_resolved:
                    key, value = executor.execute(task.name)
                    results[key] = value
                    completed_tasks.add(task)
            remainingTasks = self.getRemainingTasks(remainingTasks, completed_tasks)
        return results

    def dependenciesResolved(self, task, completed_tasks):
        dependencies_resolved = True
        for dep in task.depends_on:
            if dep not in completed_tasks:
                dependencies_resolved = False
                break
        return dependencies_resolved

    def getRemainingTasks(self, tasksList, completed_tasks):
        remainingTasks = []
        for task in tasksList:
            if task not in completed_tasks:
                remainingTasks.append(task)
        return remainingTasks