from app.task import Task
import asyncio

class LogExecutor:
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(2)
        return "logs", "user created successfully"