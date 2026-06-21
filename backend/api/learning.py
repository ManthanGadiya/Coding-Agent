from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.core.learning import LearningSystem

router = APIRouter()
system = LearningSystem()


class FailureRequest(BaseModel):
    description: str
    category: str = "internal"
    severity: str = "medium"
    impact: str
    affected_components: List[str] = []
    root_cause: str
    root_cause_confidence: str = "medium"
    resolution: str = ""
    preventive_actions: List[str] = []


class LessonCreate(BaseModel):
    topic: str
    description: str
    evidence: List[str]
    confidence: str = "medium"
    scope: str = "project"
    supporting_projects: List[str] = []
    author: str = "system"


class MetricsRequest(BaseModel):
    overall: float
    categories: Dict[str, float]


class ScoreRequest(BaseModel):
    categories: Dict[str, float]
    weights: Optional[Dict[str, float]] = None


class ImprovementProposal(BaseModel):
    observation: str
    evidence: List[str]
    expected_benefit: str
    risks: List[str] = []
    confidence: str = "medium"
    recommendation: str = ""


class ReviewRequest(BaseModel):
    decision: str
    notes: str = ""


class FiveWhysRequest(BaseModel):
    problem: str


@router.post("/failures")
def create_failure(req: FailureRequest):
    return system.record_failure(
        description=req.description, category=req.category, severity=req.severity,
        impact=req.impact, affected_components=req.affected_components,
        root_cause=req.root_cause, root_cause_confidence=req.root_cause_confidence,
        resolution=req.resolution, preventive_actions=req.preventive_actions,
    )


@router.get("/failures")
def list_failures(limit: int = 20):
    return [f.to_dict() for f in system.failures[-limit:]]


@router.post("/lessons")
def create_lesson(req: LessonCreate):
    return system.create_lesson(
        topic=req.topic, description=req.description, evidence=req.evidence,
        confidence=req.confidence, scope=req.scope,
        supporting_projects=req.supporting_projects, author=req.author,
    )


@router.get("/lessons")
def search_lessons(
    query: str = "", scope: Optional[str] = None, status: Optional[str] = None,
    confidence: Optional[str] = None, limit: int = 10,
):
    return system.search_lessons(query, scope, status, confidence, limit)


@router.post("/lessons/{lesson_id}/supersede")
def supersede_lesson(lesson_id: str, new_id: str = Query(..., description="New lesson ID")):
    return system.supersede_lesson(lesson_id, new_id)


@router.post("/lessons/{lesson_id}/promote")
def promote_lesson(lesson_id: str, scope: str = Query(..., description="New scope")):
    return system.promote_lesson(lesson_id, scope)


@router.post("/metrics")
def record_metrics(req: MetricsRequest):
    return system.record_metrics(req.overall, req.categories)


@router.get("/metrics")
def get_metrics(limit: int = 10):
    return system.get_metrics(limit)


@router.post("/metrics/score")
def score_metrics(req: ScoreRequest):
    return system.score_metrics(req.categories, req.weights)


@router.post("/proposals")
def create_proposal(req: ImprovementProposal):
    return system.propose_improvement(
        observation=req.observation, evidence=req.evidence,
        expected_benefit=req.expected_benefit, risks=req.risks,
        confidence=req.confidence, recommendation=req.recommendation,
    )


@router.get("/proposals")
def list_proposals(status: Optional[str] = None):
    result = system.proposals
    if status:
        result = [p for p in result if p.get("status") == status]
    return result


@router.post("/proposals/{proposal_id}/review")
def review_proposal(proposal_id: str, req: ReviewRequest):
    return system.review_proposal(proposal_id, req.decision, req.notes)


@router.post("/five-whys")
def five_whys(req: FiveWhysRequest):
    return system.five_whys(req.problem)
