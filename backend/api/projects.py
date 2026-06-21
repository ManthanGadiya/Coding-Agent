from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.models.project import Project, ProjectStatus
from backend.models.task import Task, TaskStatus

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    local_path: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    constraints: Optional[List[str]] = None


class ProjectUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    repository_url: Optional[str] = None
    local_path: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    status: Optional[ProjectStatus] = None
    settings: Optional[dict] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: Optional[str]
    status: ProjectStatus
    repository_url: Optional[str]
    local_path: Optional[str]
    tech_stack: Optional[List[str]]
    architecture_decisions: Optional[List[dict]]
    constraints: Optional[List[str]]
    owner_id: str
    settings: Optional[dict]
    task_count: int
    completed_task_count: int
    last_activity: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ProjectStatus] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    
    total = query.count()
    projects = query.order_by(desc(Project.updated_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, project: ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()


@router.get("/{project_id}/stats")
def get_project_stats(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_stats = db.query(
        Task.status,
        func.count(Task.id)
    ).filter(Task.project_id == project_id).group_by(Task.status).all()
    
    return {
        "project": project,
        "task_statistics": {status.value: count for status, count in task_stats},
        "completion_rate": (
            project.completed_task_count / project.task_count * 100
            if project.task_count > 0 else 0
        )
    }