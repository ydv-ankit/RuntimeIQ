from app.task import Task
import asyncio
class RepositoryExecutor:
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(122)
        return "repository", "repo cloned successfully"