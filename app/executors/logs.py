from app.task import Task
import asyncio

class LogExecutor:
    description = """
            Fetches application/service logs.
            Use when the goal requires understanding
            traces, logs and debugging.
            """
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(2)
        return "logs", "user created successfully"