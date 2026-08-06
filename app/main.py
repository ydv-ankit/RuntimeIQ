from fastapi import FastAPI
from app.models.api_models import InvestigateRequestBody
from app.runtime import Runtime

app = FastAPI()

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy"
    }

@app.post("/api/v1/investigate")
async def investigate(body: InvestigateRequestBody):
    runtime = Runtime()
    results = runtime.run(body.goal)
    return {
        "status": "started",
        "result": results
    }