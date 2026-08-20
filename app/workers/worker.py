from app.runtime import Runtime
from app.repository.run_repository import RunRepository
from app.config.redis import get_redis_connection
from app.constants import RedisEnums, LEASE_TIME
from app.workers.recovery_worker import startRecoveryWorker
import uuid
import asyncio
import time

WORKER_ID = str(uuid.uuid4())
MAX_CONCURRENT_RUNS = 2

run_semaphore = asyncio.Semaphore(MAX_CONCURRENT_RUNS)

async def execute_and_release(run_id):
    try:
        await execute_runtime(run_id)
    finally:
        run_semaphore.release()

async def renew_lease(run_id: str, lease_lost: asyncio.Event):
    while True:
        await asyncio.sleep(LEASE_TIME - 10)

        redis_conn = get_redis_connection()
        owner = await redis_conn.hget(
            RedisEnums.RUN_LEASE_OWNERS_KEY.value,
            run_id
        )

        print(
            "LEASE DEBUG:",
            "run_id =", run_id,
            "expected =", WORKER_ID,
            "actual =", owner.decode() if owner else None
        )
        result = await renew_lease_script(
            keys=[
                RedisEnums.RUN_LEASE_OWNERS_KEY.value,
                RedisEnums.RUN_LEASE_KEY.value,
            ],
            args=[
                run_id,
                WORKER_ID,
                time.time() + LEASE_TIME,
            ],
        )

        await redis_conn.close()

        if result == 0:
            print("Lost lease ownership:", run_id)
            lease_lost.set()
            return

        print("Lease renewed:", run_id)

async def execute_runtime(run_id):
    redis_conn = get_redis_connection()
    lease_lost = asyncio.Event()

    try:
        run = RunRepository.get(run_id)

        # create initial lease...
        print("setting initial lease in redis")
        await redis_conn.zadd(RedisEnums.RUN_LEASE_KEY.value, {run_id: time.time() + LEASE_TIME})
        await redis_conn.hset(RedisEnums.RUN_LEASE_OWNERS_KEY.value, run_id, WORKER_ID)

        lease_task = asyncio.create_task(
            renew_lease(run_id, lease_lost)
        )

        runtime = Runtime()

        runtime_task = asyncio.create_task(
            runtime.execute(run)
        )

        lease_lost_task = asyncio.create_task(
            lease_lost.wait()
        )

        done, pending = await asyncio.wait(
            [runtime_task, lease_lost_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        if lease_lost_task in done:
            print("Lease lost → cancelling runtime")

            runtime_task.cancel()

            try:
                await runtime_task
            except asyncio.CancelledError:
                pass

            return

        results, workflow_failed = await runtime_task

    finally:
        lease_task.cancel()
        await redis_conn.zrem(
        RedisEnums.RUN_LEASE_KEY.value,
            run_id
        )

        await redis_conn.hdel(
            RedisEnums.RUN_LEASE_OWNERS_KEY.value,
            run_id
        )

        await redis_conn.close()

async def consume_runs():
    print("==========> STARTED CONSUME RUNS <==========")
    redis_conn = get_redis_connection()
    try:
        while True:
            await run_semaphore.acquire()
            result = await redis_conn.brpop(RedisEnums.RUN_QUEUE_KEY.value, 1)
            if result is None:
                run_semaphore.release()
                continue

            run_id = result[1].decode()
            print("popped run_id", run_id)
            asyncio.create_task(
                execute_and_release(run_id)
            )
    finally:
        await redis_conn.close()

async def startWorker():
    redis_conn = get_redis_connection()
    global renew_lease_script
    with open("app/scripts/lease.lua", "r") as f:
        script = f.read()

    renew_lease_script = redis_conn.register_script(script)

    recovery_task = asyncio.create_task(startRecoveryWorker())
    consumer_task = asyncio.create_task(consume_runs())

    try:
        await asyncio.gather(
            recovery_task,
            consumer_task
        )
    finally:
        recovery_task.cancel()
        consumer_task.cancel()
        await redis_conn.close()

if __name__ == "__main__":
    asyncio.run(startWorker())
