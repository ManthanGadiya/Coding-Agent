from sqlalchemy import String, Text, Integer, Enum as SQLEnum, ForeignKey, Index, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.base import Base, TimestampMixin, UUIDMixin
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNED = "planned"
    RESEARCHING = "researching"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TaskType(str, Enum):
    RESEARCH = "research"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    DEBUGGING = "debugging"
    TESTING = "testing"
    REVIEW = "review"
    TEACHING = "teaching"
    OPTIMIZATION = "optimization"
    MAINTENANCE = "maintenance"
    MULTI_STAGE = "multi_stage"


class TaskComplexity(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


class Task(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_type: Mapped[TaskType] = mapped_column(SQLEnum(TaskType), nullable=False, index=True)
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    complexity: Mapped[TaskComplexity] = mapped_column(SQLEnum(TaskComplexity), default=TaskComplexity.SIMPLE)

    project_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    parent_task_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=True)

    assigned_agent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("workflows.id"), nullable=True)

    requirements: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    acceptance_criteria: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    dependencies: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    risks: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    estimated_effort: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actual_effort: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_tasks_project_status", "project_id", "status"),
        Index("ix_tasks_agent_status", "assigned_agent", "status"),
    )


class TaskLog(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "task_logs"

    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    agent: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(20), default="info")
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_task_logs_task_id", "task_id"),
    )