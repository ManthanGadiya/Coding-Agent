from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.agent import Agent, AgentType, AgentStatus
from backend.agents import AGENT_REGISTRY, create_agent, get_manager
from backend.core.disagreement import disagreement_engine

router = APIRouter()


class AgentCreate(BaseModel):
    agent_type: AgentType
    name: str
    description: Optional[str] = None
    capabilities: List[str] = []
    permissions: List[str] = []
    configuration: Optional[Dict[str, Any]] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    capabilities: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    configuration: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    id: str
    agent_type: str
    name: str
    description: Optional[str]
    status: str
    capabilities: List[str]
    permissions: List[str]
    current_task_id: Optional[str]
    tasks_completed: int
    tasks_failed: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Manager routes (must be before /{agent_id} routes) ---

@router.get("/registry/list")
def list_agent_types():
    return {"agent_types": list(AGENT_REGISTRY.keys())}


@router.get("/manager/status")
def get_manager_status():
    mgr = get_manager()
    return mgr._report_status({"include_agents": True}).output


@router.get("/manager/info")
def get_manager_info():
    mgr = get_manager()
    return mgr.get_status()


@router.post("/manager/route")
async def route_task(task_data: dict):
    mgr = get_manager()
    result = await mgr._route_task(task_data)
    return {"success": result.success, "output": result.output}


@router.post("/manager/workflow")
async def run_workflow(workflow_data: dict):
    mgr = get_manager()
    result = await mgr._manage_workflow(workflow_data)
    return {"success": result.success, "output": result.output}


class RunGoalRequest(BaseModel):
    goal: str
    context: Optional[Dict[str, Any]] = None


@router.post("/run-goal")
async def run_goal(req: RunGoalRequest):
    mgr = get_manager()
    result = await mgr.run_goal(req.goal, req.context)
    return result


class AutonomousRequest(BaseModel):
    poll_interval: int = 10


@router.post("/autonomous/start")
async def start_autonomous(req: AutonomousRequest):
    mgr = get_manager()
    await mgr.start_autonomous(req.poll_interval)
    return {"status": "started", "mode": "full", "poll_interval": req.poll_interval}


@router.post("/autonomous/stop")
async def stop_autonomous():
    mgr = get_manager()
    await mgr.stop_autonomous()
    return {"status": "stopped", "mode": "agent"}


@router.get("/autonomous/status")
def autonomous_status():
    mgr = get_manager()
    return {
        "mode": mgr.autonomy.mode.value,
        "running": mgr._loop_task is not None and not mgr._loop_task.done(),
    }


# --- CRUD routes ---

@router.post("", response_model=AgentResponse, status_code=201)
def create_agent_endpoint(agent: AgentCreate, db: Session = Depends(get_db)):
    db_agent = Agent(**agent.model_dump())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@router.get("", response_model=List[AgentResponse])
def list_agents(
    agent_type: Optional[AgentType] = None,
    status: Optional[AgentStatus] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Agent)
    if agent_type:
        query = query.filter(Agent.agent_type == agent_type)
    if status:
        query = query.filter(Agent.status == status)
    return query.all()


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.patch("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: str, agent: AgentUpdate, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    update_data = agent.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agent, field, value)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()


@router.get("/{agent_id}/status")
def get_agent_runtime_status(agent_id: str):
    mgr = get_manager()
    agent = mgr.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Runtime agent not found")
    return agent.get_status()


@router.post("/{agent_id}/execute")
async def execute_agent_task(agent_id: str, task_data: dict):
    mgr = get_manager()
    agent = mgr.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    from backend.agents.base import AgentTask
    task = AgentTask(**task_data)
    result = await agent.execute_task(task)
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "confidence": result.confidence,
    }


class ConflictResolveRequest(BaseModel):
    agents: List[str]
    issue: str
    arguments: Dict[str, str] = {}
    evidence: Dict[str, str] = {}
    severity: str = "medium"
    escalate: bool = False


@router.post("/conflict/resolve")
async def resolve_conflict(req: ConflictResolveRequest):
    mgr = get_manager()
    data = req.model_dump()
    for agent_id, ev in req.evidence.items():
        data[f"evidence_{agent_id}"] = ev
    result = await mgr._resolve_conflict(data)
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
    }


@router.get("/conflict/history")
def conflict_history():
    mgr = get_manager()
    return {
        "conflicts": [
            {"conflict_id": c.conflict_id, "agents": c.agents_involved,
             "topic": c.topic, "step": c.current_step.value,
             "outcome": c.outcome}
            for c in mgr.conflict_records
        ]
    }


@router.get("/communication/check")
def check_communication_path(sender: str, receiver: str):
    mgr = get_manager()
    blocked = mgr.check_communication_path(sender, receiver)
    return {"allowed": blocked is None, "sender": sender,
            "receiver": receiver, "reason": blocked}


class RecordDisagreementRequest(BaseModel):
    issue: str
    agents: List[str]
    arguments: Dict[str, str] = {}
    severity: str = "medium"


@router.post("/disagreement/record")
def record_disagreement(req: RecordDisagreementRequest):
    record = disagreement_engine.record_disagreement(req.issue, req.agents, req.arguments, req.severity)
    return {
        "id": record.id, "issue": record.issue, "agents": record.agents,
        "class": record.disagreement_class.value, "severity": record.severity,
        "user_notified": record.user_notified, "created_at": record.created_at,
    }


@router.get("/disagreement/notifications")
def get_notifications():
    pending = disagreement_engine.get_pending_notifications()
    return {"notifications": [{"id": n.id, "disagreement_id": n.disagreement_id,
                                "message": n.message, "read": n.read,
                                "acknowledged": n.acknowledged, "created_at": n.created_at}
                               for n in pending],
            "count": len(pending)}


class AcknowledgeRequest(BaseModel):
    notification_id: str
    response: Optional[str] = None


@router.post("/disagreement/acknowledge")
def acknowledge_notification(req: AcknowledgeRequest):
    n = disagreement_engine.acknowledge(req.notification_id, req.response)
    if not n:
        raise HTTPException(404, "Notification not found")
    return {"id": n.id, "acknowledged": n.acknowledged, "read": n.read}


@router.post("/disagreement/{disagreement_id}/resolve")
def resolve_disagreement(disagreement_id: str, resolution: str):
    record = disagreement_engine.resolve(disagreement_id, resolution)
    if not record:
        raise HTTPException(404, "Disagreement record not found")
    return {"id": record.id, "resolution": record.resolution, "resolved_at": record.resolved_at}


@router.get("/disagreement/unresolved")
def list_unresolved():
    records = disagreement_engine.get_unresolved()
    return {"disagreements": [{"id": r.id, "issue": r.issue, "class": r.disagreement_class.value,
                                "severity": r.severity, "agents": r.agents} for r in records],
            "count": len(records)}


@router.get("/disagreement/history")
def disagreement_history():
    return {"records": disagreement_engine.get_history()}
