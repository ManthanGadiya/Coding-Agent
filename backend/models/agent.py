from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, JSON, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.base import Base, TimestampMixin, UUIDMixin
from enum import Enum
from typing import Optional, List, Dict, Any


class AgentType(str, Enum):
    MANAGER = "manager"
    ARCHITECT = "architect"
    PLANNER = "planner"
    CODER = "coder"
    TESTER = "tester"
    DEBUGGER = "debugger"
    REVIEWER = "reviewer"
    MEMORY = "memory"


class AgentStatus(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class Agent(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "agents"

    agent_type: Mapped[AgentType] = mapped_column(SQLEnum(AgentType), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[AgentStatus] = mapped_column(SQLEnum(AgentStatus), default=AgentStatus.IDLE)

    capabilities: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    permissions: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    configuration: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    current_task_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=True)
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    tasks_failed: Mapped[int] = mapped_column(Integer, default=0)

    last_active: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_agents_type_status", "agent_type", "status"),
    )


from datetime import datetime