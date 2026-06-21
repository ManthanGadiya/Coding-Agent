from sqlalchemy import String, Text, JSON, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base, TimestampMixin, UUIDMixin
from enum import Enum
from typing import Optional, List, Dict, Any


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class User(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="user")
    skill_level: Mapped[SkillLevel] = mapped_column(SQLEnum(SkillLevel), default=SkillLevel.INTERMEDIATE)
    preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)


class UserGoal(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "user_goals"

    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    domain: Mapped[str] = mapped_column(String(100), default="general")
    status: Mapped[GoalStatus] = mapped_column(SQLEnum(GoalStatus), default=GoalStatus.ACTIVE)
    target_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
