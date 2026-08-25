from app.task import Task
import asyncio

class SummaryExecutor:
    description = """
            Give a summary of the report that
            includes details from various executors
            """
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(41)
        return "summary", "issue spotted"