from typing import Dict, List, Optional
from datetime import datetime

from backend.core.database import EngineSession
from backend.models.learning import (
    DisagreementRecord as DisagreementRecordModel,
    DisagreementClass, DisagreementNotification,
)


OPERATIONAL_KEYWORDS = ["deadlock", "tool conflict", "resource contention", "parallel write",
                        "race condition", "duplicate task", "concurrent access", "state conflict"]

STRATEGIC_KEYWORDS = ["architecture", "design", "approach", "methodology", "tradeoff",
                      "framework", "pattern", "roadmap", "technology", "standard"]


class DisagreementEngine:
    def __init__(self):
        pass

    def _db(self):
        return EngineSession()

    def classify(self, issue: str, agent_args: Dict[str, str]) -> DisagreementClass:
        topic_lower = issue.lower()
        operational_score = sum(1 for kw in OPERATIONAL_KEYWORDS if kw in topic_lower)
        strategic_score = sum(1 for kw in STRATEGIC_KEYWORDS if kw in topic_lower)
        for arg in agent_args.values():
            arg_lower = arg.lower()
            operational_score += sum(1 for kw in OPERATIONAL_KEYWORDS if kw in arg_lower)
            strategic_score += sum(1 for kw in STRATEGIC_KEYWORDS if kw in arg_lower)
        return DisagreementClass.STRATEGIC if strategic_score >= operational_score else DisagreementClass.OPERATIONAL

    def record_disagreement(self, issue: str, agents: List[str],
                            arguments: Dict[str, str], severity: str = "medium") -> DisagreementRecordModel:
        db = self._db()
        try:
            dc = self.classify(issue, arguments)
            record = DisagreementRecordModel(
                issue=issue, agents=agents,
                disagreement_class=dc, severity=severity,
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            if dc == DisagreementClass.STRATEGIC or severity in ("high", "critical"):
                self.notify_user(db, record.id, f"Strategic disagreement: {issue[:100]}")
            return record
        finally:
            db.close()

    def notify_user(self, db, disagreement_id: str, message: str) -> DisagreementNotification:
        n = DisagreementNotification(disagreement_id=disagreement_id, message=message)
        db.add(n)
        db.commit()
        db.refresh(n)
        db.query(DisagreementRecordModel).filter(
            DisagreementRecordModel.id == disagreement_id
        ).update({"user_notified": True})
        db.commit()
        return n

    def acknowledge(self, notification_id: str, response: Optional[str] = None) -> Optional[DisagreementNotification]:
        db = self._db()
        try:
            n = db.query(DisagreementNotification).filter(DisagreementNotification.id == notification_id).first()
            if not n:
                return None
            n.read = True
            n.acknowledged = True
            if response:
                db.query(DisagreementRecordModel).filter(
                    DisagreementRecordModel.id == n.disagreement_id
                ).update({"user_response": response})
            db.commit()
            return n
        finally:
            db.close()

    def resolve(self, disagreement_id: str, resolution: str) -> Optional[DisagreementRecordModel]:
        db = self._db()
        try:
            record = db.query(DisagreementRecordModel).filter(DisagreementRecordModel.id == disagreement_id).first()
            if not record:
                return None
            record.resolution = resolution
            record.resolved_at = datetime.utcnow()
            db.commit()
            return record
        finally:
            db.close()

    def get_pending_notifications(self) -> List[DisagreementNotification]:
        db = self._db()
        try:
            return db.query(DisagreementNotification).filter(DisagreementNotification.read == False).all()
        finally:
            db.close()

    def get_unresolved(self) -> List[DisagreementRecordModel]:
        db = self._db()
        try:
            return db.query(DisagreementRecordModel).filter(DisagreementRecordModel.resolution.is_(None)).all()
        finally:
            db.close()

    def get_history(self) -> List[Dict]:
        db = self._db()
        try:
            return [{"id": r.id, "issue": r.issue, "agents": r.agents,
                     "class": r.disagreement_class.value, "severity": r.severity,
                     "resolution": r.resolution, "user_notified": r.user_notified,
                     "user_response": r.user_response,
                     "created_at": r.created_at.isoformat() if r.created_at else ""}
                    for r in db.query(DisagreementRecordModel).order_by(DisagreementRecordModel.created_at.desc()).all()]
        finally:
            db.close()


disagreement_engine = DisagreementEngine()
