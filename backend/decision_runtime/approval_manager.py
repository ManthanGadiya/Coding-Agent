from typing import Any, Dict, List, Optional, Set
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field

from backend.decision_runtime.event_bus import event_bus, Event, EventPriority
from backend.decision_runtime.task_classifier import TaskType


class ApprovalScope(str, Enum):
    PUSH = "push"
    DELETE = "delete"
    BRANCH_CREATE = "branch_create"
    BRANCH_DELETE = "branch_delete"
    REPO_DELETE = "repo_delete"
    FORCE_PUSH = "force_push"
    LARGE_FS_CHANGE = "large_fs_change"
    EXTERNAL_INTEGRATION = "external_integration"
    DESTRUCTIVE_OP = "destructive_op"
    RELEASE = "release"
    DEPLOYMENT = "deployment"
    HIGH_RISK_ACTION = "high_risk_action"
    STRATEGIC_DECISION = "strategic_decision"
    ARCHITECTURAL_CHANGE = "architectural_change"
    CONSTITUTION_OVERRIDE = "constitution_override"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"


APPROVAL_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "push": {"level": "action", "risk": "medium"},
    "delete": {"level": "action", "risk": "high"},
    "branch_create": {"level": "action", "risk": "medium"},
    "branch_delete": {"level": "action", "risk": "high"},
    "repo_delete": {"level": "action", "risk": "critical"},
    "force_push": {"level": "action", "risk": "critical"},
    "large_fs_change": {"level": "action", "risk": "high"},
    "external_integration": {"level": "integration", "risk": "medium"},
    "destructive_op": {"level": "action", "risk": "critical"},
    "release": {"level": "workflow", "risk": "high"},
    "deployment": {"level": "workflow", "risk": "high"},
    "high_risk_action": {"level": "action", "risk": "high"},
    "strategic_decision": {"level": "decision", "risk": "high"},
    "architectural_change": {"level": "decision", "risk": "medium"},
    "constitution_override": {"level": "constitution", "risk": "critical"},
}


APPROVAL_BY_TASK: Dict[TaskType, List[ApprovalScope]] = {
    TaskType.DEPLOYMENT: [ApprovalScope.DEPLOYMENT, ApprovalScope.RELEASE],
    TaskType.RELEASE: [ApprovalScope.RELEASE],
    TaskType.LARGE_PROJECT: [ApprovalScope.STRATEGIC_DECISION],
    TaskType.ARCHITECTURE: [ApprovalScope.ARCHITECTURAL_CHANGE],
    TaskType.SYSTEM_DESIGN: [ApprovalScope.ARCHITECTURAL_CHANGE],
    TaskType.PROJECT_PLANNING: [ApprovalScope.STRATEGIC_DECISION],
}


@dataclass
class ApprovalRequest:
    scope: ApprovalScope
    reason: str
    data: Dict[str, Any] = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_by: str = "runtime"
    approved_by: Optional[str] = None
    response: Optional[str] = None
    created_at: str = ""
    resolved_at: Optional[str] = None


class ApprovalManager:
    def __init__(self):
        self._pending: Dict[str, ApprovalRequest] = {}
        self._history: List[ApprovalRequest] = []
        self._auto_approve_patterns: Dict[str, bool] = {}

    def requires_approval(self, scope: ApprovalScope, context: Optional[Dict] = None) -> bool:
        thresholds = APPROVAL_THRESHOLDS.get(scope.value, {})
        risk = thresholds.get("risk", "low")
        action_risk = (context or {}).get("risk", "low")
        risk_rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        return risk_rank.get(risk, 0) >= 1 or risk_rank.get(action_risk, 0) >= 2

    def check_task_approvals(self, task_type: TaskType, complexity: str) -> List[ApprovalScope]:
        scopes = APPROVAL_BY_TASK.get(task_type, [])
        if complexity in ("complex", "critical"):
            scopes.append(ApprovalScope.HIGH_RISK_ACTION)
        return list(set(scopes))

    def request(self, scope: ApprovalScope, reason: str, data: Optional[Dict] = None,
                requested_by: str = "runtime") -> ApprovalRequest:
        req = ApprovalRequest(
            scope=scope,
            reason=reason,
            data=data or {},
            requested_by=requested_by,
            created_at=datetime.utcnow().isoformat(),
        )
        request_id = f"apr-{len(self._history) + len(self._pending) + 1}"
        self._pending[request_id] = req

        event_bus.publish(Event(
            topic="approval.requested",
            source="approval_manager",
            data={
                "request_id": request_id,
                "scope": scope.value,
                "reason": reason,
                "risk": APPROVAL_THRESHOLDS.get(scope.value, {}).get("risk", "unknown"),
            },
            priority=EventPriority.HIGH,
            correlation_id=data.get("correlation_id") if data else None,
        ))
        return req

    def respond(self, request_id: str, approved: bool, by: str = "manager",
                 response: Optional[str] = None) -> Optional[ApprovalRequest]:
        req = self._pending.pop(request_id, None)
        if not req:
            return None
        req.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        req.approved_by = by
        req.response = response
        req.resolved_at = datetime.utcnow().isoformat()
        self._history.append(req)

        event_bus.publish(Event(
            topic="approval.resolved",
            source="approval_manager",
            data={
                "scope": req.scope.value,
                "approved": approved,
                "reason": req.reason,
                "response": response,
            },
            priority=EventPriority.NORMAL,
        ))
        return req

    def get_pending(self) -> Dict[str, ApprovalRequest]:
        return dict(self._pending)

    def get_history(self, limit: int = 50) -> List[ApprovalRequest]:
        return self._history[-limit:]

    def set_auto_approve(self, pattern: str, approve: bool = True):
        self._auto_approve_patterns[pattern] = approve

    def check_auto_approve(self, scope: ApprovalScope) -> Optional[bool]:
        return self._auto_approve_patterns.get(scope.value)


approval_manager = ApprovalManager()
