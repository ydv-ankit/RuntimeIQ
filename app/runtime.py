from app.planner import Planner
from app.executors.metrics import MetricExecutor
from app.executors.database import DatabaseExecutor
from app.executors.logs import LogExecutor
from app.executors.repository import RepositoryExecutor
from app.executors.summary import SummaryExecutor
from app.models.run import Run, RunStatus
from app.task import Task
from app.repository.run_repository import RunRepository
from app.config.logging import logger
from app.config.prometheus import runs_started, active_runs, runs_completed, runs_failed, run_duration
import asyncio
import time

class Runtime:
    executorsRegistry = {
        "metrics": MetricExecutor(),
        "database": DatabaseExecutor(),
        "logs": LogExecutor(),
        "repository": RepositoryExecutor(),
        "summary": SummaryExecutor()
    }

    async def execute(self, run: Run, worker_id: str):
        start_execution_time = time.monotonic()
        runs_started.inc()
        active_runs.labels(worker_id).inc()

        try:
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

            execution_context = {}

            # scheduler
            workflow_failed = False
            while remaining_tasks and not workflow_failed:
                tasks_to_execute = list()
                for task in remaining_tasks:
                    deps_resolved, deps_context = self.dependencies_resolved(task, completed_tasks, execution_context)
                    logger.info("dependencies_resolved: %s", deps_resolved)
                    logger.info("dependencies_context: %s", deps_context)
                    if deps_resolved:
                        tasks_to_execute.append([task, deps_context])
                if not tasks_to_execute:
                    raise RuntimeError("No executable tasks remain; possible cyclic dependency")
                
                executions = await asyncio.gather(
                        *(self.execute_task(task, deps_context) for task, deps_context in tasks_to_execute),
                        return_exceptions=True
                    )
                logger.info("executions: %s", executions)
                for task, execution in executions:
                    if isinstance(execution, Exception):
                        workflow_failed = True
                        logger.exception("Task failed: %s", execution)
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
            runs_completed.inc()
            end_execution_time = time.monotonic()
            execution_duration_time = end_execution_time - start_execution_time
            logger.info("execution took %s seconds", execution_duration_time)
            return results, workflow_failed
        except Exception as e:
            logger.exception("failed to execute run=%s", run.id)
            runs_failed.inc()
        finally:
            active_runs.labels(worker_id).dec()
            run_duration.observe(
                time.monotonic() - start_execution_time
            )

    def dependencies_resolved(self, task, completed_tasks, execution_context):
        dependencies_resolved = True
        context = dict()
        for dep in task.depends_on:
            if dep not in completed_tasks:
                dependencies_resolved = False
                break
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