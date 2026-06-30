from sqlalchemy import String, Text, Enum as SQLEnum, Index, JSON, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base, TimestampMixin, UUIDMixin
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE, index=True)

    repository_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    local_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    tech_stack: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    architecture_decisions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    constraints: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    owner_id: Mapped[str] = mapped_column(String(100), nullable=False, default="user")
    settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    task_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_task_count: Mapped[int] = mapped_column(Integer, default=0)

    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)

    __table_args__ = (
        Index("ix_projects_status_owner", "status", "owner_id"),
    )