from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.core.release import release_engine

router = APIRouter()


class CreateReleaseRequest(BaseModel):
    version: str
    release_type: str = "patch"


@router.get("/strategies")
def list_strategies():
    return release_engine.get_strategies()


@router.post("/candidates")
def create_candidate(req: CreateReleaseRequest):
    return release_engine.create_candidate(req.version, req.release_type)


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    rc = release_engine.get_candidate(candidate_id)
    if not rc:
        raise HTTPException(404, "Release candidate not found")
    return rc


class ApproveRequest(BaseModel):
    approved_by: str = "manager"


@router.post("/candidates/{candidate_id}/approve")
def approve_candidate(candidate_id: str, req: ApproveRequest):
    result = release_engine.approve_candidate(candidate_id, req.approved_by)
    if not result:
        raise HTTPException(404, "Release candidate not found or cannot be approved")
    return result


@router.post("/candidates/{candidate_id}/deploy")
def deploy_candidate(candidate_id: str):
    result = release_engine.deploy(candidate_id)
    if not result:
        raise HTTPException(400, "Candidate not found or not in approved state")
    return result


class RollbackRequest(BaseModel):
    reason: str


@router.post("/candidates/{candidate_id}/rollback")
def rollback_candidate(candidate_id: str, req: RollbackRequest):
    result = release_engine.rollback(candidate_id, req.reason)
    if not result:
        raise HTTPException(404, "Release candidate not found")
    return result


class CheckRequest(BaseModel):
    check_name: str
    passed: bool


@router.post("/candidates/{candidate_id}/checks")
def set_check(candidate_id: str, req: CheckRequest):
    result = release_engine.set_check(candidate_id, req.check_name, req.passed)
    if not result:
        raise HTTPException(404, "Release candidate not found")
    return result


class StrategyRequest(BaseModel):
    strategy: str


@router.post("/candidates/{candidate_id}/strategy")
def select_strategy(candidate_id: str, req: StrategyRequest):
    result = release_engine.select_strategy(candidate_id, req.strategy)
    if not result:
        raise HTTPException(404, "Candidate or strategy not found")
    return result