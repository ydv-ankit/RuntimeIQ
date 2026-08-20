from app.config.redis import get_redis_connection
from app.constants import RedisEnums
from app.repository.run_repository import RunRepository, RunStatus
from app.config.logging import logger
import time
import asyncio

async def startRecoveryWorker():
    redis_conn = get_redis_connection()
    logger.info("========> STARTED RECOVERY WORKER <========")
    try:
        while True:
            await asyncio.sleep(5)
            now = time.time()
            expired_runs = await redis_conn.zrangebyscore(RedisEnums.RUN_LEASE_KEY.value, "-inf", now)
            logger.info("expired runs: %s", expired_runs)
            for run_id in expired_runs:
                decoded_run_id = run_id.decode()
                logger.info("RUN_ID=%s", decoded_run_id)
                run = RunRepository.get(decoded_run_id)
                if run.status == RunStatus.COMPLETED:
                    logger.info("run already completed, deleting...")
                else:
                    logger.info("run not completed, requeuing...")
                    await redis_conn.lpush(RedisEnums.RUN_QUEUE_KEY.value, str(decoded_run_id))
                await redis_conn.zrem(RedisEnums.RUN_LEASE_KEY.value, decoded_run_id)
                await redis_conn.hdel(RedisEnums.RUN_LEASE_OWNERS_KEY.value, decoded_run_id)
    finally:
        await redis_conn.close()

if __name__ == "__main__":
    """
    This is recovery worker, run it with main worker
    """
    logger.info("You cannot run recovery worker directly, use worker.py")
