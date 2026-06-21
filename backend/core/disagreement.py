from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DisagreementClass(str, Enum):
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"


@dataclass
class DisagreementRecord:
    id: str
    issue: str
    agents: List[str]
    disagreement_class: DisagreementClass
    severity: str = "medium"
    resolution: Optional[str] = None
    user_notified: bool = False
    user_response: Optional[str] = None
    created_at: str = ""
    resolved_at: Optional[str] = None


@dataclass
class UserNotification:
    id: str
    disagreement_id: str
    message: str
    read: bool = False
    acknowledged: bool = False
    created_at: str = ""


OPERATIONAL_KEYWORDS = ["deadlock", "tool conflict", "resource contention", "parallel write",
                        "race condition", "duplicate task", "concurrent access", "state conflict"]

STRATEGIC_KEYWORDS = ["architecture", "design", "approach", "methodology", "tradeoff",
                      "framework", "pattern", "roadmap", "technology", "standard"]


class DisagreementEngine:
    def __init__(self):
        self.records: List[DisagreementRecord] = []
        self.notifications: List[UserNotification] = []

    def _next_id(self, prefix: str) -> str:
        return f"{prefix}-{len(self.records) + 1:04d}"

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
                            arguments: Dict[str, str], severity: str = "medium") -> DisagreementRecord:
        dc = self.classify(issue, arguments)
        now = datetime.utcnow().isoformat()
        record = DisagreementRecord(
            id=self._next_id("DGR"),
            issue=issue, agents=agents,
            disagreement_class=dc, severity=severity,
            created_at=now,
        )
        self.records.append(record)

        if dc == DisagreementClass.STRATEGIC or severity in ("high", "critical"):
            self.notify_user(record.id, f"Strategic disagreement: {issue[:100]}")
        return record

    def notify_user(self, disagreement_id: str, message: str) -> UserNotification:
        n = UserNotification(
            id=f"notif-{len(self.notifications) + 1:04d}",
            disagreement_id=disagreement_id,
            message=message,
            created_at=datetime.utcnow().isoformat(),
        )
        self.notifications.append(n)

        record = next((r for r in self.records if r.id == disagreement_id), None)
        if record:
            record.user_notified = True
        return n

    def acknowledge(self, notification_id: str, response: Optional[str] = None) -> Optional[UserNotification]:
        n = next((n for n in self.notifications if n.id == notification_id), None)
        if not n:
            return None
        n.read = True
        n.acknowledged = True
        if response:
            record = next((r for r in self.records if r.id == n.disagreement_id), None)
            if record:
                record.user_response = response
        return n

    def resolve(self, disagreement_id: str, resolution: str) -> Optional[DisagreementRecord]:
        record = next((r for r in self.records if r.id == disagreement_id), None)
        if not record:
            return None
        record.resolution = resolution
        record.resolved_at = datetime.utcnow().isoformat()
        return record

    def get_pending_notifications(self) -> List[UserNotification]:
        return [n for n in self.notifications if not n.read]

    def get_unresolved(self) -> List[DisagreementRecord]:
        return [r for r in self.records if r.resolution is None]

    def get_history(self) -> List[Dict]:
        return [
            {"id": r.id, "issue": r.issue, "agents": r.agents,
             "class": r.disagreement_class.value, "severity": r.severity,
             "resolution": r.resolution, "user_notified": r.user_notified,
             "user_response": r.user_response, "created_at": r.created_at}
            for r in self.records
        ]


disagreement_engine = DisagreementEngine()
