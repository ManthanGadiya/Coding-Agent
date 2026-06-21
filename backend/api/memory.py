from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.memory import (
    GlobalMemory, ProjectMemory, MemoryEntry,
    MemoryScope, MemoryCategory, MemoryStatus, ConfidenceLevel
)
from sqlalchemy import desc

router = APIRouter()


class GlobalMemoryCreate(BaseModel):
    category: MemoryCategory
    key: str
    value: str
    context: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    evidence: Optional[str] = None
    source_project: Optional[str] = None
    tags: Optional[List[str]] = None


class ProjectMemoryCreate(BaseModel):
    project_id: str
    category: MemoryCategory
    key: str
    value: str
    context: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    evidence: Optional[str] = None
    tags: Optional[List[str]] = None


class MemoryEntryCreate(BaseModel):
    scope: MemoryScope
    project_id: Optional[str] = None
    category: MemoryCategory
    title: str
    content: str
    summary: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    source_agent: Optional[str] = None
    evidence: Optional[str] = None
    tags: Optional[List[str]] = None
    related_entries: Optional[List[str]] = None


class MemoryEntryResponse(BaseModel):
    id: str
    scope: str
    project_id: Optional[str]
    category: str
    title: str
    content: str
    summary: Optional[str]
    confidence: str
    status: str
    source_agent: Optional[str]
    tags: Optional[List[str]]
    usage_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# Global Memory
@router.post("/global", status_code=201)
def create_global_memory(mem: GlobalMemoryCreate, db: Session = Depends(get_db)):
    entry = GlobalMemory(**mem.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/global")
def list_global_memory(
    category: Optional[MemoryCategory] = None,
    key: Optional[str] = None,
    status: MemoryStatus = MemoryStatus.ACTIVE,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(GlobalMemory).filter(GlobalMemory.status == status)
    if category:
        query = query.filter(GlobalMemory.category == category)
    if key:
        query = query.filter(GlobalMemory.key.ilike(f"%{key}%"))
    return query.order_by(desc(GlobalMemory.usage_count)).offset((page - 1) * page_size).limit(page_size).all()


# Project Memory
@router.post("/project", status_code=201)
def create_project_memory(mem: ProjectMemoryCreate, db: Session = Depends(get_db)):
    entry = ProjectMemory(**mem.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/project/{project_id}")
def list_project_memory(
    project_id: str,
    category: Optional[MemoryCategory] = None,
    key: Optional[str] = None,
    status: MemoryStatus = MemoryStatus.ACTIVE,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ProjectMemory).filter(
        ProjectMemory.project_id == project_id,
        ProjectMemory.status == status
    )
    if category:
        query = query.filter(ProjectMemory.category == category)
    if key:
        query = query.filter(ProjectMemory.key.ilike(f"%{key}%"))
    return query.order_by(desc(ProjectMemory.usage_count)).offset((page - 1) * page_size).limit(page_size).all()


# Memory Entries
@router.post("/entries", response_model=MemoryEntryResponse, status_code=201)
def create_memory_entry(entry: MemoryEntryCreate, db: Session = Depends(get_db)):
    db_entry = MemoryEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.get("/entries", response_model=List[MemoryEntryResponse])
def list_memory_entries(
    scope: Optional[MemoryScope] = None,
    project_id: Optional[str] = None,
    category: Optional[MemoryCategory] = None,
    status: MemoryStatus = MemoryStatus.ACTIVE,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(MemoryEntry).filter(MemoryEntry.status == status)
    if scope:
        query = query.filter(MemoryEntry.scope == scope)
    if project_id:
        query = query.filter(MemoryEntry.project_id == project_id)
    if category:
        query = query.filter(MemoryEntry.category == category)
    return query.order_by(desc(MemoryEntry.created_at)).offset((page - 1) * page_size).limit(page_size).all()


@router.get("/entries/{entry_id}", response_model=MemoryEntryResponse)
def get_memory_entry(entry_id: str, db: Session = Depends(get_db)):
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    entry.usage_count += 1
    db.commit()
    return entry


@router.patch("/entries/{entry_id}", response_model=MemoryEntryResponse)
def update_memory_entry(entry_id: str, update: dict, db: Session = Depends(get_db)):
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    for field, value in update.items():
        if hasattr(entry, field):
            setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/entries/{entry_id}", status_code=204)
def delete_memory_entry(entry_id: str, db: Session = Depends(get_db)):
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    db.delete(entry)
    db.commit()


@router.get("/search")
def search_memory(
    q: str,
    scope: Optional[MemoryScope] = None,
    project_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(MemoryEntry).filter(
        MemoryEntry.status == MemoryStatus.ACTIVE,
        (MemoryEntry.title.ilike(f"%{q}%")) | (MemoryEntry.content.ilike(f"%{q}%")) | (MemoryEntry.summary.ilike(f"%{q}%"))
    )
    if scope:
        query = query.filter(MemoryEntry.scope == scope)
    if project_id:
        query = query.filter(MemoryEntry.project_id == project_id)
    return query.order_by(MemoryEntry.confidence.desc()).limit(limit).all()