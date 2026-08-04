from pydantic import BaseModel

class InvestigateRequestBody(BaseModel):
    goal: str