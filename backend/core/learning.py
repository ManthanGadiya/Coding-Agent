from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class FailureSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FailureCategory(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    PROCESS = "process"
    KNOWLEDGE = "knowledge"
    TOOL = "tool"
    WORKFLOW = "workflow"


class LessonStatus(str, Enum):
    ACTIVE = "active"
    HISTORICAL = "historical"
    SUPERSEDED = "superseded"


class LessonScope(str, Enum):
    PROJECT = "project"
    PROJECT_TYPE = "project_type"
    GLOBAL = "global"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FailureRecord:
    failure_id: str
    description: str
    category: FailureCategory
    severity: FailureSeverity
    impact: str
    affected_components: List[str]
    root_cause: str
    root_cause_confidence: Confidence
    resolution: str
    preventive_actions: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        return {k: v.value if isinstance(v, Enum) else v for k, v in self.__dict__.items()}


@dataclass
class Lesson:
    lesson_id: str
    topic: str
    description: str
    supporting_projects: List[str]
    evidence: List[str]
    confidence: Confidence
    status: LessonStatus = LessonStatus.ACTIVE
    scope: LessonScope = LessonScope.PROJECT
    author: str = "system"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        return {k: v.value if isinstance(v, Enum) else v for k, v in self.__dict__.items()}


@dataclass
class MetricSnapshot:
    timestamp: str
    overall: float
    categories: Dict[str, float]


class LearningSystem:
    def __init__(self):
        self.failures: List[FailureRecord] = []
        self.lessons: List[Lesson] = []
        self.metrics: List[MetricSnapshot] = []
        self.proposals: List[Dict] = []
        self._failure_counter = 0
        self._lesson_counter = 0

    def record_failure(self, description: str, category: str, severity: str, impact: str,
                       affected_components: List[str], root_cause: str,
                       root_cause_confidence: str = "medium",
                       resolution: str = "", preventive_actions: Optional[List[str]] = None) -> Dict:
        self._failure_counter += 1
        record = FailureRecord(
            failure_id=f"FAIL-{self._failure_counter:04d}",
            description=description,
            category=FailureCategory(category),
            severity=FailureSeverity(severity),
            impact=impact,
            affected_components=affected_components,
            root_cause=root_cause,
            root_cause_confidence=Confidence(root_cause_confidence),
            resolution=resolution,
            preventive_actions=preventive_actions or [],
        )
        self.failures.append(record)

        if record.root_cause_confidence in (Confidence.HIGH, Confidence.MEDIUM):
            self._auto_generate_lesson(record)

        return record.to_dict()

    def _auto_generate_lesson(self, failure: FailureRecord) -> Optional[Lesson]:
        topic = f"Prevent: {failure.root_cause[:80]}"
        description = f"Failure #{failure.failure_id}: {failure.description}\nRoot cause: {failure.root_cause}"
        lesson = Lesson(
            lesson_id=f"LESSON-{self._lesson_counter + 1:04d}",
            topic=topic,
            description=description,
            supporting_projects=[],
            evidence=[f"Failure {failure.failure_id}: {failure.description}", f"Root cause: {failure.root_cause}"],
            confidence=failure.root_cause_confidence,
        )
        self._lesson_counter += 1
        self.lessons.append(lesson)
        return lesson

    def create_lesson(self, topic: str, description: str, evidence: List[str],
                      confidence: str = "medium", scope: str = "project",
                      supporting_projects: Optional[List[str]] = None,
                      author: str = "system") -> Dict:
        self._lesson_counter += 1
        lesson = Lesson(
            lesson_id=f"LESSON-{self._lesson_counter:04d}",
            topic=topic,
            description=description,
            supporting_projects=supporting_projects or [],
            evidence=evidence,
            confidence=Confidence(confidence),
            scope=LessonScope(scope),
            author=author,
        )
        self.lessons.append(lesson)
        return lesson.to_dict()

    def search_lessons(self, query: str = "", scope: Optional[str] = None,
                       status: Optional[str] = None, confidence: Optional[str] = None,
                       limit: int = 10) -> List[Dict]:
        results = self.lessons
        if scope:
            results = [l for l in results if l.scope.value == scope]
        if status:
            results = [l for l in results if l.status.value == status]
        if confidence:
            results = [l for l in results if l.confidence.value == confidence]
        if query:
            q = query.lower()
            results = [l for l in results if q in l.topic.lower() or q in l.description.lower()]
        return [l.to_dict() for l in results[-limit:]]

    def supersede_lesson(self, lesson_id: str, new_lesson_id: str) -> Dict:
        for l in self.lessons:
            if l.lesson_id == lesson_id:
                l.status = LessonStatus.SUPERSEDED
                l.updated_at = datetime.utcnow().isoformat()
                return {"lesson_id": lesson_id, "new_status": "superseded", "superseded_by": new_lesson_id}
        return {"error": f"Lesson {lesson_id} not found"}

    def promote_lesson(self, lesson_id: str, new_scope: str) -> Dict:
        for l in self.lessons:
            if l.lesson_id == lesson_id:
                old = l.scope.value
                l.scope = LessonScope(new_scope)
                l.updated_at = datetime.utcnow().isoformat()
                return {"lesson_id": lesson_id, "old_scope": old, "new_scope": new_scope}
        return {"error": f"Lesson {lesson_id} not found"}

    def record_metrics(self, overall: float, categories: Dict[str, float]) -> Dict:
        snapshot = MetricSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            overall=overall,
            categories=categories,
        )
        self.metrics.append(snapshot)
        return {"timestamp": snapshot.timestamp, "overall": overall, "categories": categories}

    def get_metrics(self, limit: int = 10) -> List[Dict]:
        return [{"timestamp": m.timestamp, "overall": m.overall, "categories": m.categories}
                for m in self.metrics[-limit:]]

    def score_metrics(self, categories: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> Dict:
        default_weights = {
            "correctness": 0.25, "quality": 0.20, "reliability": 0.15,
            "testing": 0.10, "research": 0.10, "learning": 0.08,
            "governance": 0.07, "efficiency": 0.05,
        }
        w = weights or default_weights
        overall = sum(categories.get(k, 0) * v for k, v in w.items())
        thresholds = {
            "correctness": {"target": 90, "warning": 75, "critical": 60},
            "quality": {"target": 85, "warning": 70, "critical": 55},
            "reliability": {"target": 85, "warning": 70, "critical": 50},
            "testing": {"target": 80, "warning": 65, "critical": 50},
            "governance": {"target": 90, "warning": 75, "critical": 60},
        }
        alerts = []
        for cat, score in categories.items():
            t = thresholds.get(cat)
            if t and score < t["critical"]:
                alerts.append({"category": cat, "level": "critical", "score": score, "threshold": t["critical"]})
            elif t and score < t["warning"]:
                alerts.append({"category": cat, "level": "warning", "score": score, "threshold": t["warning"]})
        return {"overall": round(overall, 1), "categories": categories, "alerts": alerts}

    def propose_improvement(self, observation: str, evidence: List[str],
                            expected_benefit: str, risks: List[str],
                            confidence: str = "medium", recommendation: str = "") -> Dict:
        proposal = {
            "proposal_id": f"IMP-{len(self.proposals) + 1:04d}",
            "observation": observation,
            "evidence": evidence,
            "expected_benefit": expected_benefit,
            "risks": risks,
            "confidence": confidence,
            "recommendation": recommendation or expected_benefit,
            "status": "proposed",
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.proposals.append(proposal)
        return proposal

    def review_proposal(self, proposal_id: str, decision: str, notes: str = "") -> Dict:
        for p in self.proposals:
            if p["proposal_id"] == proposal_id:
                p["status"] = decision
                p["review_notes"] = notes
                p["reviewed_at"] = datetime.utcnow().isoformat()
                return p
        return {"error": f"Proposal {proposal_id} not found"}

    def five_whys(self, problem: str) -> List[Dict]:
        lines = problem.strip().split("\n")
        whys = []
        for i, line in enumerate(lines):
            if i == 0:
                whys.append({"level": 0, "question": "Problem", "answer": line.strip()})
            else:
                whys.append({"level": i, "question": f"Why? ({i}/5)", "answer": line.strip()})
        return whys
