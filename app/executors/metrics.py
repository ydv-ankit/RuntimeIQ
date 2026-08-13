from app.task import Task
import asyncio

class MetricExecutor:
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(2)
        # raise RuntimeError("this is intentional error message")
        return "metrics", "424ms"