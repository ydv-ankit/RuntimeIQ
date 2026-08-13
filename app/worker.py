from app.runtime import Runtime
from app.repository.run_repository import RunRepository
from app.config.redis import get_redis_connection
from app.constants import RedisEnums
from app.models.run import Run, RunStatus
import asyncio

async def executeRuntime(run_id: str):
    run = RunRepository.get(run_id)
    if run.status == RunStatus.COMPLETED:
        run.__repr__()
        print("Run already completed, skipping...")
        return
    runtime = Runtime()
    results, workflow_failed = await runtime.execute(run)
    run.__repr__()

def consumer():
    redis_conn = get_redis_connection()
    while True:
        run_id = redis_conn.brpop(RedisEnums.RUN_QUEUE.value, 0)
        print("popped run_id", run_id)
        asyncio.run(executeRuntime(run_id[1].decode()))

if __name__ == "__main__":
    consumer()