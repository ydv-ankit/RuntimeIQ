from app.planner import Planner
from app.models.run import Run, RunStatus
from app.task import Task
from app.repository.run_repository import RunRepository
from app.repository.workflow_repository import WorkflowRepository
from app.config.logging import logger
from app.config.prometheus import runs_started, active_runs, runs_completed, runs_failed, run_duration
from app.workflows.parser import WorkflowParser, Workflow
from app.workflows.validator import WorkflowValidator
import asyncio
import time

class Runtime:
    def __init__(self, executor_registry):
        self.executor_registry = executor_registry

    async def execute(self, run: Run, workflow: Workflow, worker_id: str):
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
            workflow_tasks = workflow.tasks
            
            completed_tasks = set()
            remaining_tasks: list[Task] = self.get_remaining_tasks(workflow_tasks, completed_tasks)

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
                    completed_tasks.add(task.name)
                    execution_context[task.name] = execution
                    results["COMPLETED"][task.name] = execution


                remaining_tasks = self.get_remaining_tasks(remaining_tasks, completed_tasks)

            if workflow_failed:
                run.status = RunStatus.FAILED
                runs_failed.inc()
            else:
                run.status = RunStatus.COMPLETED
                runs_completed.inc()

            RunRepository.update_status(run.id, run.status)
            end_execution_time = time.monotonic()
            execution_duration_time = end_execution_time - start_execution_time
            logger.info("execution took %s seconds", execution_duration_time)
            return results, workflow_failed
        except Exception:
            logger.exception("failed to execute run=%s", run.id)
            runs_failed.inc()
            run.status = RunStatus.FAILED
            RunRepository.update_status(run.id, run.status)
            raise
        finally:
            active_runs.labels(worker_id).dec()
            run_duration.observe(
                time.monotonic() - start_execution_time
            )

    def dependencies_resolved(self, task: Task, completed_tasks: set, execution_context: dict):
        context = dict()
        for dep in task.depends_on:
            if dep not in completed_tasks:
                return False, {}
            context[dep] = execution_context[dep]
        return True, context

    def get_remaining_tasks(self, tasksList: list[Task], completed_tasks: set[str]):
        remainingTasks = []
        for task in tasksList:
            if task.name not in completed_tasks:
                remainingTasks.append(task)
        return remainingTasks

    async def execute_task(self, task: Task, deps_context: dict):
        try:
            executor = self.executor_registry.get(task.executor)

            key, value = await executor.execute(
                task.name,
                deps_context,
            )

            return task, {key: value}

        except Exception as e:
            return task, e