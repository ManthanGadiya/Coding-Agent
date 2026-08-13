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
    objective: Optional[str] = None
    context: Optional[str] = None
    options: List[OptionInput] = []
    decision_type: DecisionType = DecisionType.OPERATIONAL
    constraints: List[str] = []
    evidence: List[str] = []


@router.post("/decide")
def make_decision(req: DecisionRequest):
    result = engine.decide(
        objective=req.objective or req.context or "",
        options=[o.model_dump() for o in req.options],
        decision_type=req.decision_type,
        constraints=req.constraints,
        evidence=req.evidence,
    )
    return result


@router.get("/history")
def decision_history(limit: int = 10):
    return engine.get_history(limit)


class RiskAssessmentRequest(BaseModel):
    action: Optional[str] = None
    description: Optional[str] = None
    impact: Optional[float] = None
    likelihood: Optional[float] = None


@router.post("/assess-risk")
def assess_risk(req: Optional[RiskAssessmentRequest] = None,
                description: str = "unknown action", impact: float = 0.5, likelihood: float = 0.5):
    if req:
        description = req.action or req.description or description
        impact = req.impact if req.impact is not None else impact
        likelihood = req.likelihood if req.likelihood is not None else likelihood
    return engine.assess_risk(description, impact, likelihood)
