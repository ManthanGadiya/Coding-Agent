from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.models.workflow import Workflow, WorkflowStatus, WorkflowType, WorkflowStep
from backend.agents.manager import ManagerAgent
from backend.core.workflow_engine import (
    get_workflow_blueprint, classify_task, ComplexityLevel,
    WORKFLOW_BUILDERS, WorkflowBlueprint,
    evaluate_quality_gate, evaluate_completion_criteria,
    get_workflow_for_complexity, workflow_controller,
)
from backend.core.release import release_engine

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

    model_config = {"from_attributes": True}


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


class ExecutorRunRequest(BaseModel):
    name: str
    context: Dict[str, Any] = {}


@router.post("/executor/run")
async def executor_run(req: ExecutorRunRequest):
    from backend.decision_runtime.workflow_executor import workflow_executor
    result = await workflow_executor.execute_async(req.name, req.context)
    return result


@router.get("/executor/instances")
def executor_instances(status: Optional[str] = None):
    from backend.decision_runtime.workflow_executor import workflow_executor
    return {"instances": workflow_executor.list_instances(status)}


@router.get("/executor/instances/{instance_id}")
def executor_instance(instance_id: str):
    from backend.decision_runtime.workflow_executor import workflow_executor
    state = workflow_executor.get_state(instance_id)
    if not state:
        raise HTTPException(404, "Instance not found")
    return state


@router.post("/executor/instances/{instance_id}/pause")
def executor_pause(instance_id: str):
    from backend.decision_runtime.workflow_executor import workflow_executor
    ok = workflow_executor.pause(instance_id)
    if not ok:
        raise HTTPException(400, "Instance not running or not found")
    return {"status": "paused"}


@router.post("/executor/instances/{instance_id}/resume")
def executor_resume(instance_id: str):
    from backend.decision_runtime.workflow_executor import workflow_executor
    ok = workflow_executor.resume(instance_id)
    if not ok:
        raise HTTPException(400, "Instance not paused or not found")
    return {"status": "resumed"}


@router.post("/executor/instances/{instance_id}/cancel")
def executor_cancel(instance_id: str):
    from backend.decision_runtime.workflow_executor import workflow_executor
    ok = workflow_executor.cancel(instance_id)
    if not ok:
        raise HTTPException(400, "Instance not found")
    return {"status": "cancelled"}


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


class QualityGateRequest(BaseModel):
    checks: List[Dict[str, Any]]


@router.post("/quality-gate")
def evaluate_quality(req: QualityGateRequest):
    return evaluate_quality_gate(req.checks)


class CompletionCriteriaRequest(BaseModel):
    requirements_met: bool = False
    architecture_verified: bool = False
    implementation_complete: bool = False
    tests_passed: bool = False
    review_passed: bool = False
    documentation_updated: bool = False
    memory_updated: bool = False
    risks_documented: bool = False
    has_security_issues: bool = False
    has_architecture_issues: bool = False
    constitution_violation: bool = False


@router.post("/completion-check")
def check_completion(req: CompletionCriteriaRequest):
    return evaluate_completion_criteria(req.model_dump())


@router.get("/recommend")
def recommend_workflow(scope: str = "medium", risk: str = "low",
                       dependencies: int = 0, architecture_impact: bool = False,
                       security_impact: bool = False, research_needed: bool = False):
    complexity = classify_task(scope, risk, dependencies, architecture_impact,
                               security_impact, research_needed)
    workflow_name = get_workflow_for_complexity(complexity)
    blueprint = get_workflow_blueprint(workflow_name, complexity.value)
    return {
        "complexity": complexity.value,
        "recommended_workflow": workflow_name,
        "steps": [{"name": s.name, "agent": s.agent, "description": s.description}
                  for s in blueprint.steps] if blueprint else [],
    }


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.query(WorkflowStep).filter(WorkflowStep.workflow_id == workflow_id).delete()
    db.delete(wf)
    db.commit()


class PipelineCreateRequest(BaseModel):
    category: str
    complexity: str = "moderate"
    severity: Optional[str] = None
    impact: Optional[str] = None
    release_type: Optional[str] = None


@router.post("/pipeline")
def create_pipeline(req: PipelineCreateRequest):
    kwargs = {}
    if req.severity: kwargs["severity"] = req.severity
    if req.impact: kwargs["impact"] = req.impact
    if req.release_type: kwargs["release_type"] = req.release_type
    if req.complexity not in [c.value for c in ComplexityLevel]:
        raise HTTPException(400, f"Invalid complexity: {req.complexity}")
    smallest = workflow_controller.enforce_smallest_workflow(req.category, ComplexityLevel(req.complexity))
    pipe = workflow_controller.create_pipeline(smallest, req.complexity, **kwargs)
    return {
        "id": pipe.id, "category": pipe.category, "complexity": pipe.complexity.value,
        "state": pipe.state.value, "steps": pipe.steps,
        "enforced_workflow": smallest,
    }


class StepTransitionRequest(BaseModel):
    status: str = "completed"
    output: Dict[str, Any] = {}
    error: Optional[str] = None


@router.post("/pipeline/{pipeline_id}/transition")
def transition_pipeline(pipeline_id: str, req: StepTransitionRequest):
    result = {"status": req.status, "output": req.output}
    if req.error:
        result["error"] = req.error
    pipe = workflow_controller.transition(pipeline_id, result)
    if not pipe:
        raise HTTPException(404, "Pipeline not found")
    return {
        "id": pipe.id, "current_step": pipe.current_step,
        "total_steps": len(pipe.steps), "state": pipe.state.value,
        "errors": pipe.errors,
    }


@router.get("/pipeline/{pipeline_id}")
def get_pipeline(pipeline_id: str):
    pipe = workflow_controller.get_status(pipeline_id)
    if not pipe:
        raise HTTPException(404, "Pipeline not found")
    return {
        "id": pipe.id, "category": pipe.category, "complexity": pipe.complexity.value,
        "state": pipe.state.value, "current_step": pipe.current_step,
        "total_steps": len(pipe.steps), "steps": pipe.steps,
        "results": pipe.results, "errors": pipe.errors,
    }


@router.get("/pipeline/list/active")
def list_active_pipelines():
    pipes = workflow_controller.list_active()
    return {"pipelines": [{"id": p.id, "category": p.category, "state": p.state.value,
                            "current_step": p.current_step, "total_steps": len(p.steps)}
                           for p in pipes], "count": len(pipes)}


@router.post("/pipeline/{pipeline_id}/unblock")
def unblock_pipeline(pipeline_id: str):
    pipe = workflow_controller.unblock(pipeline_id)
    if not pipe:
        raise HTTPException(404, "Pipeline not found")
    return {"id": pipe.id, "state": pipe.state.value}


@router.post("/pipeline/{pipeline_id}/rollback")
def rollback_pipeline(pipeline_id: str):
    pipe = workflow_controller.rollback(pipeline_id)
    if not pipe:
        raise HTTPException(404, "Pipeline not found")
    return {"id": pipe.id, "state": pipe.state.value, "current_step": pipe.current_step}


class ReleaseCreateRequest(BaseModel):
    version: str
    release_type: str = "patch"


@router.post("/release/candidate")
def create_release_candidate(req: ReleaseCreateRequest):
    rc = release_engine.create_candidate(req.version, req.release_type)
    return release_engine.get_candidate(rc.id)


@router.post("/release/candidate/{candidate_id}/check")
def set_release_check(candidate_id: str, check_name: str, passed: bool = True):
    rc = release_engine.set_check(candidate_id, check_name, passed)
    if not rc:
        raise HTTPException(404, "Release candidate not found")
    return {"checks": rc.checks}


@router.post("/release/candidate/{candidate_id}/approve")
def approve_release(candidate_id: str, approved_by: str = "manager"):
    rc = release_engine.approve_candidate(candidate_id, approved_by)
    if not rc:
        raise HTTPException(404, "Release candidate not found")
    return release_engine.get_candidate(candidate_id)


@router.post("/release/candidate/{candidate_id}/deploy")
def deploy_release(candidate_id: str):
    rc = release_engine.deploy(candidate_id)
    if not rc:
        raise HTTPException(404, "Release candidate not found")
    return release_engine.get_candidate(candidate_id)


@router.post("/release/candidate/{candidate_id}/rollback")
def rollback_release(candidate_id: str, reason: str = "manual rollback"):
    rc = release_engine.rollback(candidate_id, reason)
    if not rc:
        raise HTTPException(404, "Release candidate not found")
    return release_engine.get_candidate(candidate_id)


@router.get("/release/candidate/{candidate_id}")
def get_release_candidate(candidate_id: str):
    rc = release_engine.get_candidate(candidate_id)
    if not rc:
        raise HTTPException(404, "Release candidate not found")
    return rc


@router.get("/release/strategies")
def list_rollback_strategies():
    return {"strategies": release_engine.get_strategies()}


@router.post("/release/candidate/{candidate_id}/strategy")
def select_rollback_strategy(candidate_id: str, strategy: str = "full_rollback"):
    rc = release_engine.select_strategy(candidate_id, strategy)
    if not rc:
        raise HTTPException(404, "Release candidate or strategy not found")
    return release_engine.get_candidate(candidate_id)