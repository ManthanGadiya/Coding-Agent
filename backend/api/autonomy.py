from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel
from backend.core.autonomy import AutonomyController, AutonomyMode, CAPABILITY_REGISTRY

router = APIRouter()
controller = AutonomyController()


class SetModeRequest(BaseModel):
    mode: AutonomyMode


class CheckActionRequest(BaseModel):
    action: str
    role: str
    session_id: str
    project_id: Optional[str] = ""
    confidence: str = "medium"


class GrantRequest(BaseModel):
    session_id: Optional[str] = None
    project_id: Optional[str] = None
    capabilities: list[str]


class TempCapabilityRequest(BaseModel):
    capability: str
    agent_id: str
    task_id: str
    reason: str
    duration_minutes: int = 60


@router.post("/temporary/request")
def request_temporary_capability(req: TempCapabilityRequest):
    return controller.request_temporary_capability(
        capability=req.capability, agent_id=req.agent_id,
        task_id=req.task_id, reason=req.reason,
        duration_minutes=req.duration_minutes,
    )


@router.get("/temporary/grants")
def list_temporary_grants(agent_id: str = "", task_id: str = ""):
    return {"grants": controller.get_temporary_grants(agent_id, task_id)}


@router.post("/temporary/revoke-expired")
def revoke_expired_temporary_grants():
    revoked = controller.revoke_expired_temporary_grants()
    return {"revoked": revoked}


@router.get("/mode")
def get_mode():
    return {"mode": controller.mode.value}


@router.post("/mode")
def set_mode(req: SetModeRequest):
    return controller.set_mode(req.mode)


@router.post("/check")
def check_action(req: CheckActionRequest):
    return controller.can_execute(
        action=req.action,
        role=req.role,
        session_id=req.session_id,
        project_id=req.project_id,
        confidence=req.confidence,
    )


@router.get("/capabilities/{role}")
def get_role_capabilities(role: str):
    caps = controller.permissions.get_role_capabilities(role)
    return {"role": role, "capabilities": caps}


@router.get("/registry")
def get_capability_registry():
    return {k: {"risk": v.risk.value, "approval_class": v.approval_class.value, "description": v.description}
            for k, v in CAPABILITY_REGISTRY.items()}


@router.post("/grant/session")
def grant_session(req: GrantRequest):
    return controller.approvals.grant_session(req.session_id, req.capabilities)


@router.post("/grant/project")
def grant_project(req: GrantRequest):
    return controller.approvals.grant_project(req.project_id, req.capabilities)


@router.post("/revoke/session/{session_id}")
def revoke_session(session_id: str):
    return controller.approvals.revoke_session(session_id)


@router.post("/revoke/project/{project_id}")
def revoke_project(project_id: str):
    return controller.approvals.revoke_project(project_id)


@router.get("/audit")
def audit_log(limit: int = 20):
    return controller.approvals.get_audit_log(limit)
