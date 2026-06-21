from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.agent import Agent, AgentType, AgentStatus
from backend.agents import AGENT_REGISTRY, create_agent, get_orchestrator

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

    class Config:
        from_attributes = True


# --- Orchestrator-specific routes (must be before /{agent_id} routes) ---

@router.get("/registry/list")
def list_agent_types():
    return {"agent_types": list(AGENT_REGISTRY.keys())}


@router.get("/orchestrator/status")
def get_orchestrator_status():
    orch = get_orchestrator()
    return orch._report_status({"include_agents": True}).output


@router.get("/orchestrator/info")
def get_orchestrator_info():
    orch = get_orchestrator()
    return orch.get_status()


@router.post("/orchestrator/route")
async def route_task(task_data: dict):
    orch = get_orchestrator()
    result = await orch._route_task(task_data)
    return {"success": result.success, "output": result.output}


@router.post("/orchestrator/workflow")
async def run_workflow(workflow_data: dict):
    orch = get_orchestrator()
    result = await orch._manage_workflow(workflow_data)
    return {"success": result.success, "output": result.output}


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
    orch = get_orchestrator()
    agent = orch.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Runtime agent not found")
    return agent.get_status()


@router.post("/{agent_id}/execute")
async def execute_agent_task(agent_id: str, task_data: dict):
    orch = get_orchestrator()
    agent = orch.get_agent(agent_id)
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