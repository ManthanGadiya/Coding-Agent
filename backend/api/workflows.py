from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.models.workflow import Workflow, WorkflowStatus, WorkflowType, WorkflowStep
from backend.agents.manager import ManagerAgent
from backend.core.workflow_engine import (
    get_workflow_blueprint, classify_task, ComplexityLevel, WorkflowCategory,
    WORKFLOW_BUILDERS, WorkflowBlueprint,
)

router = APIRouter()


class StepDefinition(BaseModel):
    agent_id: str
    task_type: str
    description: str
    input_data: Dict[str, Any] = {}
    critical: bool = False


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_type: WorkflowType = WorkflowType.SIMPLE
    project_id: Optional[str] = None
    steps: List[StepDefinition] = []
    metadata: Optional[Dict[str, Any]] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    steps: Optional[List[StepDefinition]] = None
    metadata: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    workflow_type: str
    status: str
    project_id: Optional[str]
    steps: list
    current_step: int
    total_steps: int
    assigned_agents: list
    completed_agents: list
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=WorkflowResponse, status_code=201)
def create_workflow(wf: WorkflowCreate, db: Session = Depends(get_db)):
    step_dicts = [s.model_dump() for s in wf.steps]
    assigned_agents = list(set(s.agent_id for s in wf.steps))

    db_wf = Workflow(
        name=wf.name,
        description=wf.description,
        workflow_type=wf.workflow_type,
        project_id=wf.project_id,
        steps=step_dicts,
        total_steps=len(step_dicts),
        assigned_agents=assigned_agents,
        extra_metadata=wf.metadata
    )
    db.add(db_wf)
    db.commit()
    db.refresh(db_wf)

    for i, step in enumerate(wf.steps):
        db_step = WorkflowStep(
            workflow_id=db_wf.id,
            step_number=i + 1,
            agent_type=step.agent_id,
            action=step.task_type,
            description=step.description,
            input_data=step.input_data
        )
        db.add(db_step)
    db.commit()
    db.refresh(db_wf)
    return db_wf


@router.get("", response_model=List[WorkflowResponse])
def list_workflows(
    project_id: Optional[str] = None,
    status: Optional[WorkflowStatus] = None,
    workflow_type: Optional[WorkflowType] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Workflow)
    if project_id:
        query = query.filter(Workflow.project_id == project_id)
    if status:
        query = query.filter(Workflow.status == status)
    if workflow_type:
        query = query.filter(Workflow.workflow_type == workflow_type)
    return query.order_by(Workflow.created_at.desc()).all()


@router.get("/categories")
def list_categories():
    return {"categories": list(WORKFLOW_BUILDERS.keys())}


class BlueprintRequest(BaseModel):
    category: str
    complexity: str = "moderate"
    severity: Optional[str] = None
    impact: Optional[str] = None
    release_type: Optional[str] = None


@router.post("/blueprint")
def generate_blueprint(req: BlueprintRequest):
    kwargs = {}
    if req.severity: kwargs["severity"] = req.severity
    if req.impact: kwargs["impact"] = req.impact
    if req.release_type: kwargs["release_type"] = req.release_type
    bp = get_workflow_blueprint(req.category, req.complexity, **kwargs)
    if not bp:
        raise HTTPException(status_code=400, detail=f"Unknown workflow category: {req.category}")
    return {
        "category": bp.category.value,
        "complexity": bp.complexity.value,
        "steps": [{"name": s.name, "agent": s.agent, "description": s.description} for s in bp.steps],
        "quality_gates": bp.quality_gates,
        "requires_approval": bp.requires_approval,
        "requires_architect": bp.requires_architect,
        "requires_reviewer": bp.requires_reviewer,
    }


class ClassifyRequest(BaseModel):
    scope: str = "medium"
    risk: str = "medium"
    dependencies: int = 0
    architecture_impact: bool = False
    security_impact: bool = False
    research_needed: bool = False


@router.post("/classify")
def classify(req: ClassifyRequest):
    c = classify_task(req.scope, req.risk, req.dependencies,
                      req.architecture_impact, req.security_impact, req.research_needed)
    return {"complexity": c.value}


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: str, wf: WorkflowUpdate, db: Session = Depends(get_db)):
    db_wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    update_data = wf.model_dump(exclude_unset=True)
    if "steps" in update_data and update_data["steps"] is not None:
        update_data["steps"] = [s.model_dump() if hasattr(s, 'model_dump') else s for s in update_data["steps"]]
        update_data["total_steps"] = len(update_data["steps"])
        update_data["assigned_agents"] = list(set(s.get("agent_id", "") for s in update_data["steps"]))
    for field, value in update_data.items():
        if field == "metadata":
            field = "extra_metadata"
        setattr(db_wf, field, value)
    db.commit()
    db.refresh(db_wf)
    return db_wf


@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    wf.status = WorkflowStatus.RUNNING
    wf.started_at = datetime.utcnow()
    db.commit()

    mgr = ManagerAgent()
    result = await mgr.run_workflow(workflow_id, wf.steps)

    if result.success:
        wf.status = WorkflowStatus.COMPLETED
        wf.completed_at = datetime.utcnow()
    else:
        wf.status = WorkflowStatus.FAILED
        wf.error = result.error
        wf.completed_at = datetime.utcnow()

    wf.result = str(result.output) if result.output else None
    db.commit()
    db.refresh(wf)

    return {"workflow": wf, "execution_result": {"success": result.success, "output": result.output}}


@router.post("/{workflow_id}/pause")
def pause_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if wf.status != WorkflowStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Only running workflows can be paused")
    wf.status = WorkflowStatus.PAUSED
    db.commit()
    return {"status": "paused"}


@router.post("/{workflow_id}/resume")
async def resume_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if wf.status != WorkflowStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Only paused workflows can be resumed")
    wf.status = WorkflowStatus.RUNNING
    db.commit()

    mgr = ManagerAgent()
    remaining_steps = wf.steps[wf.current_step:]
    result = await mgr.run_workflow(f"{workflow_id}-resume", remaining_steps)

    if result.success:
        wf.status = WorkflowStatus.COMPLETED
        wf.completed_at = datetime.utcnow()
    else:
        wf.status = WorkflowStatus.FAILED
        wf.error = result.error

    db.commit()
    db.refresh(wf)
    return {"workflow": wf, "execution_result": {"success": result.success}}


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.query(WorkflowStep).filter(WorkflowStep.workflow_id == workflow_id).delete()
    db.delete(wf)
    db.commit()