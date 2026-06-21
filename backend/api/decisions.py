from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from backend.core.decision_engine import DecisionEngine, DecisionType

router = APIRouter()
engine = DecisionEngine()


class OptionInput(BaseModel):
    label: str
    description: Optional[str] = None
    maintainability: int = 5
    complexity: int = 5
    risk: str = "medium"
    cost: int = 5
    correctness: int = 5


class DecisionRequest(BaseModel):
    objective: str
    options: List[OptionInput]
    decision_type: DecisionType = DecisionType.OPERATIONAL
    constraints: List[str] = []
    evidence: List[str] = []


@router.post("/decide")
def make_decision(req: DecisionRequest):
    result = engine.decide(
        objective=req.objective,
        options=[o.model_dump() for o in req.options],
        decision_type=req.decision_type,
        constraints=req.constraints,
        evidence=req.evidence,
    )
    return result


@router.get("/history")
def decision_history(limit: int = 10):
    return engine.get_history(limit)


@router.post("/assess-risk")
def assess_risk(description: str, impact: float = 0.5, likelihood: float = 0.5):
    return engine.assess_risk(description, impact, likelihood)
