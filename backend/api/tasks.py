from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.models.task import Task, TaskStatus, TaskType, TaskComplexity, TaskLog
from backend.agents.orchestrator import OrchestratorAgent

router = APIRouter()


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: TaskType = TaskType.IMPLEMENTATION
    project_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    requirements: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    estimated_effort: Optional[int] = None
    complexity: TaskComplexity = TaskComplexity.SIMPLE


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assigned_agent: Optional[str] = None
    workflow_id: Optional[str] = None
    requirements: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    estimated_effort: Optional[int] = None
    actual_effort: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    task_type: str
    status: str
    complexity: str
    project_id: Optional[str]
    parent_task_id: Optional[str]
    assigned_agent: Optional[str]
    workflow_id: Optional[str]
    estimated_effort: Optional[int]
    actual_effort: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskLogResponse(BaseModel):
    id: str
    task_id: str
    agent: str
    action: str
    message: str
    level: str
    created_at: datetime


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    project_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None,
    assigned_agent: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    if task_type:
        query = query.filter(Task.task_type == task_type)
    if assigned_agent:
        query = query.filter(Task.assigned_agent == assigned_agent)
    tasks = query.order_by(desc(Task.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = task.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "metadata":
            field = "extra_metadata"
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


@router.post("/{task_id}/classify")
def classify_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    orchestrator = OrchestratorAgent()
    result = orchestrator._classify_task({"description": task.description or task.title})
    complexity = orchestrator._assess_complexity({"description": task.description or task.title})
    return {"classification": result.output, "complexity": complexity.output}


@router.get("/{task_id}/logs", response_model=List[TaskLogResponse])
def get_task_logs(task_id: str, db: Session = Depends(get_db)):
    return db.query(TaskLog).filter(TaskLog.task_id == task_id).order_by(TaskLog.created_at).all()


@router.post("/{task_id}/logs", response_model=TaskLogResponse, status_code=201)
def add_task_log(task_id: str, log: dict, db: Session = Depends(get_db)):
    db_log = TaskLog(task_id=task_id, **log)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log