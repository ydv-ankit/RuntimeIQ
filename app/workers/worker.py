from app.runtime import Runtime
from app.repository.run_repository import RunRepository
from app.config.redis import get_redis_connection
from app.constants import RedisEnums, LEASE_TIME
from app.models.run import Run, RunStatus
from app.workers.recovery_worker import startRecoveryWorker
import uuid
import asyncio
import time

WORKER_ID = str(uuid.uuid4())

async def renew_lease(run_id: str):
    while True:
        print(f"sleeping for {LEASE_TIME - 10} time")
        await asyncio.sleep(LEASE_TIME - 10)
        print("awake...")
        redis_conn = get_redis_connection()
        redis_conn.zadd(RedisEnums.RUN_LEASE_KEY.value, {run_id: time.time() + LEASE_TIME})
        print("updated lease time")
        redis_conn.close()

async def executeRuntime(run_id: str):
    redis_conn = get_redis_connection()
    try:
        run = RunRepository.get(run_id)
        if run.status == RunStatus.COMPLETED:
            run.__repr__()
            print("Run already completed, skipping...")
            return

        print("setting initial lease")
        redis_conn.zadd(RedisEnums.RUN_LEASE_KEY.value, {run_id: time.time() + LEASE_TIME})
        redis_conn.hset(RedisEnums.RUN_LEASE_OWNERS_KEY.value, run_id, WORKER_ID)

        lease_task = asyncio.create_task(
            renew_lease(run_id)
        )

        runtime = Runtime()
        results, workflow_failed = await runtime.execute(run)
        run.__repr__()
        lease_task.cancel()
        redis_conn.zrem(RedisEnums.RUN_LEASE_KEY.value, run_id)
        redis_conn.hdel(RedisEnums.RUN_LEASE_OWNERS_KEY.value, run_id)
    except Exception as e:
        print("error occured in runtime")
        print(e)
        raise
    finally:
        print("finally completed...")
        lease_task.cancel()
        redis_conn.close()

def consume_runs():
    print("==========> STARTED CONSUME RUNS <==========")
    redis_conn = get_redis_connection()
    try:
        while True:
            run_id = redis_conn.brpop(RedisEnums.RUN_QUEUE_KEY.value, 0)    # 0 timeout -> continously wait for queue item
            print("popped run_id", run_id)
            asyncio.run(executeRuntime(run_id[1].decode()))
    finally:
        redis_conn.close()

async def startWorker():
    recovery_task = asyncio.create_task(startRecoveryWorker())
    consumer_task = asyncio.to_thread(consume_runs)

    try:
        await asyncio.gather(recovery_task, consumer_task)
    finally:
        recovery_task.cancel()

if __name__ == "__main__":
    asyncio.run(startWorker())
