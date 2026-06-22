from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from backend.core.database import EngineSession
from backend.models.learning import (
    FailureRecord as FailureRecordModel, FailureCategory, FailureSeverity, Confidence,
    Lesson as LessonModel, LessonStatus, LessonScope,
    MetricSnapshot as MetricSnapshotModel,
    Proposal as ProposalModel,
    KnowledgeArtifact as KnowledgeArtifactModel, ArtifactStatus,
    CandidateRule as CandidateRuleModel,
)


class LearningSystem:
    def __init__(self):
        self._failure_counter = 0
        self._lesson_counter = 0

    def _db(self):
        return EngineSession()

    def record_failure(self, description: str, category: str, severity: str, impact: str,
                       affected_components: List[str], root_cause: str,
                       root_cause_confidence: str = "medium",
                       resolution: str = "", preventive_actions: Optional[List[str]] = None) -> Dict:
        db = self._db()
        try:
            record = FailureRecordModel(
                description=description, category=FailureCategory(category),
                severity=FailureSeverity(severity), impact=impact,
                affected_components=affected_components, root_cause=root_cause,
                root_cause_confidence=Confidence(root_cause_confidence),
                resolution=resolution, preventive_actions=preventive_actions or [],
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            if record.root_cause_confidence in (Confidence.HIGH, Confidence.MEDIUM):
                self._auto_generate_lesson(db, record)

            return {
                "failure_id": record.id, "description": record.description,
                "category": record.category.value, "severity": record.severity.value,
                "root_cause": record.root_cause, "timestamp": record.created_at.isoformat() if record.created_at else "",
            }
        finally:
            db.close()

    def _auto_generate_lesson(self, db, failure: FailureRecordModel):
        topic = f"Prevent: {failure.root_cause[:80]}"
        description = f"Failure #{failure.id}: {failure.description}\nRoot cause: {failure.root_cause}"
        lesson = LessonModel(
            topic=topic, description=description,
            evidence=[f"Failure {failure.id}: {failure.description}", f"Root cause: {failure.root_cause}"],
            confidence=failure.root_cause_confidence,
        )
        db.add(lesson)
        db.commit()

    def create_lesson(self, topic: str, description: str, evidence: List[str],
                      confidence: str = "medium", scope: str = "project",
                      supporting_projects: Optional[List[str]] = None,
                      author: str = "system") -> Dict:
        db = self._db()
        try:
            lesson = LessonModel(
                topic=topic, description=description,
                supporting_projects=supporting_projects or [], evidence=evidence,
                confidence=Confidence(confidence), scope=LessonScope(scope), author=author,
            )
            db.add(lesson)
            db.commit()
            db.refresh(lesson)
            return {
                "lesson_id": lesson.id, "topic": lesson.topic,
                "confidence": lesson.confidence.value, "scope": lesson.scope.value,
                "status": lesson.status.value, "created_at": lesson.created_at.isoformat() if lesson.created_at else "",
            }
        finally:
            db.close()

    def search_lessons(self, query: str = "", scope: Optional[str] = None,
                       status: Optional[str] = None, confidence: Optional[str] = None,
                       limit: int = 10) -> List[Dict]:
        db = self._db()
        try:
            q = db.query(LessonModel)
            if scope:
                q = q.filter(LessonModel.scope == LessonScope(scope))
            if status:
                q = q.filter(LessonModel.status == LessonStatus(status))
            if confidence:
                q = q.filter(LessonModel.confidence == Confidence(confidence))
            if query:
                like = f"%{query.lower()}%"
                q = q.filter(LessonModel.topic.ilike(like) | LessonModel.description.ilike(like))
            results = q.order_by(LessonModel.created_at.desc()).limit(limit).all()
            return [{
                "lesson_id": r.id, "topic": r.topic, "description": r.description[:200],
                "confidence": r.confidence.value, "scope": r.scope.value,
                "status": r.status.value, "author": r.author,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            } for r in results]
        finally:
            db.close()

    def supersede_lesson(self, lesson_id: str, new_lesson_id: str) -> Dict:
        db = self._db()
        try:
            lesson = db.query(LessonModel).filter(LessonModel.id == lesson_id).first()
            if not lesson:
                return {"error": f"Lesson {lesson_id} not found"}
            lesson.status = LessonStatus.SUPERSEDED
            lesson.superseded_by = new_lesson_id
            db.commit()
            return {"lesson_id": lesson_id, "new_status": "superseded", "superseded_by": new_lesson_id}
        finally:
            db.close()

    def promote_lesson(self, lesson_id: str, new_scope: str) -> Dict:
        db = self._db()
        try:
            lesson = db.query(LessonModel).filter(LessonModel.id == lesson_id).first()
            if not lesson:
                return {"error": f"Lesson {lesson_id} not found"}
            old = lesson.scope.value
            lesson.scope = LessonScope(new_scope)
            db.commit()
            return {"lesson_id": lesson_id, "old_scope": old, "new_scope": new_scope}
        finally:
            db.close()

    def record_metrics(self, overall: float, categories: Dict[str, float]) -> Dict:
        db = self._db()
        try:
            snap = MetricSnapshotModel(overall=overall, categories=categories)
            db.add(snap)
            db.commit()
            return {"timestamp": snap.created_at.isoformat() if snap.created_at else "", "overall": overall, "categories": categories}
        finally:
            db.close()

    def get_metrics(self, limit: int = 10) -> List[Dict]:
        db = self._db()
        try:
            results = db.query(MetricSnapshotModel).order_by(MetricSnapshotModel.created_at.desc()).limit(limit).all()
            return [{"timestamp": r.created_at.isoformat() if r.created_at else "", "overall": r.overall, "categories": r.categories} for r in results]
        finally:
            db.close()

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
        db = self._db()
        try:
            prop = ProposalModel(
                observation=observation, evidence=evidence,
                expected_benefit=expected_benefit, risks=risks,
                confidence=Confidence(confidence), recommendation=recommendation or expected_benefit,
            )
            db.add(prop)
            db.commit()
            db.refresh(prop)
            return {
                "proposal_id": prop.id, "observation": prop.observation,
                "expected_benefit": prop.expected_benefit, "confidence": prop.confidence.value,
                "status": prop.status, "timestamp": prop.created_at.isoformat() if prop.created_at else "",
            }
        finally:
            db.close()

    @property
    def proposals(self) -> List[Dict]:
        db = self._db()
        try:
            return [{
                "proposal_id": p.id, "observation": p.observation,
                "expected_benefit": p.expected_benefit, "confidence": p.confidence.value,
                "status": p.status, "timestamp": p.created_at.isoformat() if p.created_at else "",
            } for p in db.query(ProposalModel).order_by(ProposalModel.created_at.desc()).all()]
        finally:
            db.close()

    def review_proposal(self, proposal_id: str, decision: str, notes: str = "") -> Dict:
        db = self._db()
        try:
            prop = db.query(ProposalModel).filter(ProposalModel.id == proposal_id).first()
            if not prop:
                return {"error": f"Proposal {proposal_id} not found"}
            prop.status = decision
            prop.review_notes = notes
            prop.reviewed_at = datetime.utcnow()
            db.commit()
            return {"proposal_id": prop.id, "status": decision, "review_notes": notes}
        finally:
            db.close()

    def five_whys(self, problem: str) -> List[Dict]:
        lines = problem.strip().split("\n")
        whys = []
        for i, line in enumerate(lines):
            if i == 0:
                whys.append({"level": 0, "question": "Problem", "answer": line.strip()})
            else:
                whys.append({"level": i, "question": f"Why? ({i}/5)", "answer": line.strip()})
        return whys
