from app.task import Task
import asyncio

class DatabaseExecutor:
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(2)
        return "database", "run this sql"