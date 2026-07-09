from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.models.memory import (
    GlobalMemory, ProjectMemory, MemoryEntry,
    MemoryScope, MemoryCategory, MemoryStatus, ConfidenceLevel,
)
from backend.core.retention import retention_engine
from backend.core.compression import memory_compressor
from sqlalchemy import desc

router = APIRouter()

def _auto_retention_check(db: Session):
    count = db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.ACTIVE).count()
    if count > 200:
        retention_engine.health_metrics([{"id": str(e.id), "usage_count": getattr(e, "usage_count", 0),
            "confidence": e.confidence.value if hasattr(e.confidence, "value") else str(e.confidence),
            "extra_metadata": e.extra_metadata or {}}
            for e in db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.ACTIVE).all()])


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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Global Memory
@router.post("/global", status_code=201)
def create_global_memory(mem: GlobalMemoryCreate, db: Session = Depends(get_db)):
    entry = GlobalMemory(**mem.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    _auto_retention_check(db)
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
    _auto_retention_check(db)
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
    _auto_retention_check(db)
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
    meta = entry.extra_metadata or {}
    versions = meta.get("versions", [])
    version_num = len(versions) + 1
    snapshot = {
        "version": version_num,
        "title": entry.title,
        "content_preview": entry.content[:200] if entry.content else "",
        "status": entry.status.value,
        "confidence": entry.confidence.value,
        "timestamp": datetime.utcnow().isoformat(),
        "changes": list(update.keys()),
    }
    versions.append(snapshot)
    meta["versions"] = versions
    meta["current_version"] = version_num
    entry.extra_metadata = meta

    for field, value in update.items():
        if hasattr(entry, field):
            setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/entries/{entry_id}/versions")
def get_entry_versions(entry_id: str, db: Session = Depends(get_db)):
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    meta = entry.extra_metadata or {}
    return {
        "entry_id": entry_id,
        "current_version": meta.get("current_version", 0),
        "versions": meta.get("versions", []),
    }


@router.delete("/entries/{entry_id}", status_code=204)
def delete_memory_entry(entry_id: str, db: Session = Depends(get_db)):
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    db.delete(entry)
    db.commit()


class CompressRequest(BaseModel):
    entry_ids: List[str]
    level: int = 1


@router.post("/compress")
def compress_memories(req: CompressRequest, db: Session = Depends(get_db)):
    from backend.core.compression import memory_compressor

    entries = db.query(MemoryEntry).filter(MemoryEntry.id.in_(req.entry_ids)).all()
    if not entries:
        raise HTTPException(404, "No entries found")

    entry_dicts = [{"id": e.id, "title": e.title, "content": e.content,
                     "category": e.category.value, "tags": e.tags}
                   for e in entries]
    result = memory_compressor.compress(entry_dicts, level=req.level)

    for e in entries:
        meta = e.extra_metadata or {}
        meta["compression_level"] = req.level
        meta["compressed_at"] = result.created_at
        meta["source_compression_ids"] = result.source_ids
        e.extra_metadata = meta
    db.commit()

    return {"compression_level": req.level, "source_count": len(entries),
            "output": result.output, "timestamp": result.created_at}


@router.post("/compress/suggest")
def suggest_compression(db: Session = Depends(get_db)):
    from backend.core.compression import memory_compressor

    entries = db.query(MemoryEntry).filter(
        MemoryEntry.status == MemoryStatus.ACTIVE
    ).all()
    entry_dicts = [{"id": e.id, "title": e.title, "content": e.content,
                     "category": e.category.value, "tags": e.tags}
                   for e in entries]
    suggestions = memory_compressor.suggest_patterns(entry_dicts)
    return {"suggestions": suggestions, "total_entries": len(entries)}


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


@router.get("/retention/score/{entry_id}")
def get_retention_score(entry_id: str, db: Session = Depends(get_db)):
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(404, "Entry not found")
    score = retention_engine.score_entry({
        "id": entry.id, "usage_count": getattr(entry, "usage_count", 0),
        "confidence": entry.confidence.value if hasattr(entry.confidence, "value") else entry.confidence,
        "extra_metadata": entry.extra_metadata or {},
        "last_accessed": entry.last_accessed.isoformat() if getattr(entry, "last_accessed", None) else None,
    })
    return score.__dict__


@router.get("/retention/stale")
def list_stale_entries(db: Session = Depends(get_db)):
    entries = db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.ACTIVE).all()
    stale = retention_engine.get_stale_entries([
        {"id": e.id, "usage_count": getattr(e, "usage_count", 0),
         "confidence": e.confidence.value if hasattr(e.confidence, "value") else e.confidence,
         "extra_metadata": e.extra_metadata or {},
         "last_accessed": e.last_accessed.isoformat() if getattr(e, "last_accessed", None) else None}
        for e in entries
    ])
    return {"stale": [s.__dict__ for s in stale], "count": len(stale)}


@router.get("/retention/archival-candidates")
def list_archival_candidates(db: Session = Depends(get_db)):
    entries = db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.ACTIVE).all()
    candidates = retention_engine.get_archival_candidates([
        {"id": e.id, "usage_count": getattr(e, "usage_count", 0),
         "confidence": e.confidence.value if hasattr(e.confidence, "value") else e.confidence,
         "extra_metadata": e.extra_metadata or {},
         "last_accessed": e.last_accessed.isoformat() if getattr(e, "last_accessed", None) else None}
        for e in entries
    ])
    return {"candidates": candidates, "count": len(candidates)}


@router.get("/stats")
def memory_stats(db: Session = Depends(get_db)):
    active = db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.ACTIVE).count()
    archived = db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.ARCHIVED).count()
    global_count = db.query(GlobalMemory).count()
    project_count = db.query(ProjectMemory).count()
    return {"entries": active, "archived": archived, "global": global_count, "project": project_count, "total": active + archived + global_count + project_count}


@router.get("/retention/health")
def retention_health(db: Session = Depends(get_db)):
    entries = db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.ACTIVE).all()
    metrics = retention_engine.health_metrics([
        {"id": e.id, "usage_count": getattr(e, "usage_count", 0),
         "confidence": e.confidence.value if hasattr(e.confidence, "value") else e.confidence,
         "extra_metadata": e.extra_metadata or {},
         "last_accessed": e.last_accessed.isoformat() if getattr(e, "last_accessed", None) else None}
        for e in entries
    ])
    return metrics