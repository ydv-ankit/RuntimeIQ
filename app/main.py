from fastapi import FastAPI
from app.models.api_models import InvestigateRequestBody
from .planner import Planner
from .executor import Executor

app = FastAPI()

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy"
    }

@app.post("/api/v1/investigate")
async def investigate(body: InvestigateRequestBody):
    goal = body.goal
    planner = Planner()
    plan = planner.plan(goal.lower())
    print("generated plan:", plan)
    executor = Executor()
    for task in plan:
        print(executor.execute(task))
    return {
        "status": "started",
        "goal": body.goal,
        "tasks": plan
    }