from fastapi import FastAPI
from app.models.api_models import InvestigateRequestBody
from app.runtime import Runtime
from app.models.run import Run, RunStatus
from app.seed.db_seed import seed_db_schema
from app.config.redis import get_redis_connection
from app.constants import RedisEnums
from app.repository.run_repository import RunRepository 

seed_db_schema()

app = FastAPI()

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy"
    }

@app.post("/api/v1/investigate")
async def investigate(body: InvestigateRequestBody):
    goal = body.goal
    if goal is None or not isinstance(goal, str):
        return {
            "status": "failed",
            "result": {},
            "message": "invalid goal"
        }
    run = Run(goal)
    RunRepository.create(run)
    async with get_redis_connection() as redis_conn:
        await redis_conn.lpush(RedisEnums.RUN_QUEUE_KEY.value, str(run.id))
    return