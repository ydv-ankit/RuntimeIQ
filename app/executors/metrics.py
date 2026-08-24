from app.task import Task
import asyncio

class MetricExecutor:
    description = """
        Fetches application/service metrics.
        Use when the goal requires understanding
        performance, latency, throughput, errors,
        or resource utilization.
        """
    async def execute(self, task: Task, ctx: dict):
        await asyncio.sleep(100)
        # raise RuntimeError("this is intentional error message")
        return "metrics", "424ms"