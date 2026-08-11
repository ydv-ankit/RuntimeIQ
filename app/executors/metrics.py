from app.task import Task
import asyncio

class MetricExecutor:
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(2)
        return "metrics", "424ms"