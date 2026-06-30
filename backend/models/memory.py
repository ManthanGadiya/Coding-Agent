from sqlalchemy import String, Text, Integer, Enum as SQLEnum, Index, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base, TimestampMixin, UUIDMixin
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class MemoryScope(str, Enum):
    GLOBAL = "global"
    PROJECT = "project"


class MemoryCategory(str, Enum):
    PREFERENCE = "preference"
    KNOWLEDGE = "knowledge"
    DECISION = "decision"
    LESSON = "lesson"
    MISTAKE = "mistake"
    RISK = "risk"
    CONSTRAINT = "constraint"
    WORKFLOW = "workflow"
    ARCHITECTURE = "architecture"
    TECHNOLOGY = "technology"
    BUG = "bug"
    IMPROVEMENT = "improvement"
    REQUIREMENT = "requirement"
    DEPENDENCY = "dependency"
    RESEARCH = "research"
    OPTIMIZATION = "optimization"
    TECHNICAL_DEBT = "technical_debt"
    DISCOVERY = "discovery"
    MILESTONE = "milestone"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    HISTORICAL = "historical"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GlobalMemory(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "global_memory"

    category: Mapped[MemoryCategory] = mapped_column(SQLEnum(MemoryCategory), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[ConfidenceLevel] = mapped_column(SQLEnum(ConfidenceLevel), default=ConfidenceLevel.MEDIUM)
    status: Mapped[MemoryStatus] = mapped_column(SQLEnum(MemoryStatus), default=MemoryStatus.ACTIVE)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_project: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_global_memory_category_key", "category", "key"),
        Index("ix_global_memory_status", "status"),
    )


class ProjectMemory(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "project_memory"

    project_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[MemoryCategory] = mapped_column(SQLEnum(MemoryCategory), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[ConfidenceLevel] = mapped_column(SQLEnum(ConfidenceLevel), default=ConfidenceLevel.MEDIUM)
    status: Mapped[MemoryStatus] = mapped_column(SQLEnum(MemoryStatus), default=MemoryStatus.ACTIVE)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_project_memory_project_category_key", "project_id", "category", "key"),
        Index("ix_project_memory_project_status", "project_id", "status"),
    )


class MemoryEntry(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "memory_entries"

    scope: Mapped[MemoryScope] = mapped_column(SQLEnum(MemoryScope), nullable=False, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    category: Mapped[MemoryCategory] = mapped_column(SQLEnum(MemoryCategory), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[ConfidenceLevel] = mapped_column(SQLEnum(ConfidenceLevel), default=ConfidenceLevel.MEDIUM)
    status: Mapped[MemoryStatus] = mapped_column(SQLEnum(MemoryStatus), default=MemoryStatus.ACTIVE)
    source_agent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    related_entries: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_memory_entries_scope_project_category", "scope", "project_id", "category"),
        Index("ix_memory_entries_status", "status"),
    )