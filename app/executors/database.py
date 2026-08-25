from app.task import Task
import asyncio

class DatabaseExecutor:
    description = """
            Fetches data from database.
            Use when the goal requires making
            database related queries.
            """
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(2)
        return "database", "run this sql"