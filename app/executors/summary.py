from app.task import Task
import asyncio

class SummaryExecutor:
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(2)
        return "summary", "issue spotted"