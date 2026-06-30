from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, JSON, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base, TimestampMixin, UUIDMixin
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowType(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"
    FEATURE_DEVELOPMENT = "feature_development"
    BUG_FIXING = "bug_fixing"
    RELEASE = "release"
    REFACTORING = "refactoring"


class Workflow(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    workflow_type: Mapped[WorkflowType] = mapped_column(SQLEnum(WorkflowType), nullable=False, index=True)
    status: Mapped[WorkflowStatus] = mapped_column(SQLEnum(WorkflowStatus), default=WorkflowStatus.PENDING, index=True)

    project_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    initiated_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    steps: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, default=0)

    assigned_agents: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    completed_agents: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)

    __table_args__ = (
        Index("ix_workflows_project_status", "project_id", "status"),
        Index("ix_workflows_type_status", "workflow_type", "status"),
    )


class WorkflowStep(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "workflow_steps"

    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id"), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_type: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="pending")
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_workflow_steps_workflow_step", "workflow_id", "step_number"),
    )