from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from backend.config.settings import get_settings
from backend.models.base import Base
from backend.models.agent import Agent, AgentType
from typing import Generator

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
EngineSession = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

SEED_AGENTS = [
    {"agent_type": AgentType.MANAGER, "name": "Manager Agent", "description": "Central coordinator — task orchestration, conflict resolution, progress tracking", "capabilities": ["route_task", "assign_agent", "monitor_progress", "resolve_conflict", "manage_workflow", "report_status", "classify_task", "assess_complexity"]},
    {"agent_type": AgentType.ARCHITECT, "name": "Architect Agent", "description": "System design — architecture, technology selection, tradeoff analysis, risk assessment", "capabilities": ["architecture_design", "technology_selection", "tradeoff_analysis", "risk_assessment", "scalability_evaluation", "architecture_review", "system_design"]},
    {"agent_type": AgentType.PLANNER, "name": "Planner Agent", "description": "Research and planning — requirement analysis, task decomposition, plan generation, effort estimation", "capabilities": ["research", "requirement_analysis", "task_decomposition", "plan_generation", "risk_analysis", "effort_estimation", "roadmap_creation"]},
    {"agent_type": AgentType.CODER, "name": "Coder Agent", "description": "Implementation — write code, refactor, create integrations", "capabilities": ["implementation", "refactoring", "code_generation", "integration", "documentation"]},
    {"agent_type": AgentType.TESTER, "name": "Tester Agent", "description": "Validation — unit testing, integration testing, regression testing", "capabilities": ["testing", "verification", "quality_checks", "regression_testing"]},
    {"agent_type": AgentType.DEBUGGER, "name": "Debugger Agent", "description": "Failure investigation — root cause analysis, error diagnosis, recovery recommendations", "capabilities": ["debugging", "root_cause_analysis", "error_diagnosis", "recovery_planning"]},
    {"agent_type": AgentType.REVIEWER, "name": "Reviewer Agent", "description": "Quality assurance — code review, security review, maintainability review", "capabilities": ["code_review", "security_review", "quality_assurance", "maintainability_review"]},
    {"agent_type": AgentType.MEMORY, "name": "Memory Agent", "description": "Knowledge preservation — store, retrieve, organize project and global knowledge", "capabilities": ["memory_storage", "memory_retrieval", "knowledge_organization", "memory_search"]},
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Agent).count()
        if existing == 0:
            for data in SEED_AGENTS:
                agent = Agent(**data)
                db.add(agent)
            db.commit()
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
