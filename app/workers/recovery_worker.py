from app.config.redis import get_redis_connection
from app.constants import RedisEnums
from app.repository.run_repository import RunRepository, RunStatus
import time
import asyncio

async def startRecoveryWorker():
    redis_conn = get_redis_connection()
    print("========> STARTED RECOVERY WORKER <========")
    try:
        while True:
            await asyncio.sleep(5)
            now = time.time()
            expired_runs = redis_conn.zrangebyscore(RedisEnums.RUN_LEASE_KEY.value, "-inf", now)
            print("expired runs", expired_runs)
            for run_id in expired_runs:
                decoded_run_id = run_id.decode()
                print("RUN_ID:", decoded_run_id)
                print("checking db status")
                run = RunRepository.get(decoded_run_id)
                if run.status == RunStatus.COMPLETED:
                    print("run already completed, deleting...")
                else:
                    print("run not completed, requeuing...")
                    redis_conn.lpush(RedisEnums.RUN_QUEUE_KEY.value, str(decoded_run_id))
                redis_conn.zrem(RedisEnums.RUN_LEASE_KEY.value, decoded_run_id)
                redis_conn.hdel(RedisEnums.RUN_LEASE_OWNERS_KEY.value, decoded_run_id)
    finally:
        redis_conn.close()

if __name__ == "__main__":
    """
    This is recovery worker, run it with main worker
    """
    print("You cannot run recovery worker directly, use worker.py")
