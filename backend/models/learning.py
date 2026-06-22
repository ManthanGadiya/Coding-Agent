from sqlalchemy import String, Text, Integer, Float, Enum as SQLEnum, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base, TimestampMixin, UUIDMixin
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class FailureSeverity(str, Enum):
    LOW = "low"; MEDIUM = "medium"; HIGH = "high"; CRITICAL = "critical"


class FailureCategory(str, Enum):
    INTERNAL = "internal"; EXTERNAL = "external"; PROCESS = "process"
    KNOWLEDGE = "knowledge"; TOOL = "tool"; WORKFLOW = "workflow"


class LessonStatus(str, Enum):
    ACTIVE = "active"; HISTORICAL = "historical"; SUPERSEDED = "superseded"


class LessonScope(str, Enum):
    PROJECT = "project"; PROJECT_TYPE = "project_type"; GLOBAL = "global"


class Confidence(str, Enum):
    HIGH = "high"; MEDIUM = "medium"; LOW = "low"


class ArtifactStatus(str, Enum):
    OBSERVATION = "observation"; PATTERN = "pattern"
    KNOWLEDGE_ARTIFACT = "knowledge_artifact"
    CANDIDATE_RULE = "candidate_rule"
    APPROVED_RULE = "approved_rule"; SUPERSEDED = "superseded"


class DisagreementClass(str, Enum):
    OPERATIONAL = "operational"; STRATEGIC = "strategic"


class FailureRecord(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "failures"
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[FailureCategory] = mapped_column(SQLEnum(FailureCategory), nullable=False)
    severity: Mapped[FailureSeverity] = mapped_column(SQLEnum(FailureSeverity), nullable=False)
    impact: Mapped[str] = mapped_column(Text, nullable=False)
    affected_components: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause_confidence: Mapped[Confidence] = mapped_column(SQLEnum(Confidence), default=Confidence.MEDIUM)
    resolution: Mapped[str] = mapped_column(Text, default="")
    preventive_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)


class Lesson(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "lessons"
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_projects: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    evidence: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Confidence] = mapped_column(SQLEnum(Confidence), default=Confidence.MEDIUM)
    status: Mapped[LessonStatus] = mapped_column(SQLEnum(LessonStatus), default=LessonStatus.ACTIVE)
    scope: Mapped[LessonScope] = mapped_column(SQLEnum(LessonScope), default=LessonScope.PROJECT)
    author: Mapped[str] = mapped_column(String(100), default="system")
    superseded_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


class MetricSnapshot(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "metric_snapshots"
    overall: Mapped[float] = mapped_column(Float, nullable=False)
    categories: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)


class Proposal(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "proposals"
    observation: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    expected_benefit: Mapped[str] = mapped_column(Text, nullable=False)
    risks: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Confidence] = mapped_column(SQLEnum(Confidence), default=Confidence.MEDIUM)
    recommendation: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="proposed")
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class KnowledgeArtifact(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "knowledge_artifacts"
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ArtifactStatus] = mapped_column(SQLEnum(ArtifactStatus), default=ArtifactStatus.OBSERVATION)
    evidence: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source_count: Mapped[int] = mapped_column(Integer, default=1)
    conclusion: Mapped[str] = mapped_column(Text, default="")
    reusable: Mapped[bool] = mapped_column(default=False)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    source_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)


class CandidateRule(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "candidate_rules"
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    review_status: Mapped[str] = mapped_column(String(20), default="pending")
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class DisagreementRecord(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "disagreements"
    issue: Mapped[str] = mapped_column(Text, nullable=False)
    agents: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    disagreement_class: Mapped[DisagreementClass] = mapped_column(SQLEnum(DisagreementClass), default=DisagreementClass.OPERATIONAL)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_notified: Mapped[bool] = mapped_column(default=False)
    user_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class DisagreementNotification(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "disagreement_notifications"
    disagreement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(default=False)
    acknowledged: Mapped[bool] = mapped_column(default=False)


class ReleaseCandidate(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "release_candidates"
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    release_type: Mapped[str] = mapped_column(String(20), default="patch")
    state: Mapped[str] = mapped_column(String(20), default="draft")
    checks: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rollback_strategy: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rollback_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rollback_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
