from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from backend.decision_runtime.event_bus import event_bus, Event, EventPriority
from backend.decision_runtime.decision_trace import decision_trace


class EscalationLevel(int, Enum):
    AGENT_TO_AGENT = 1
    AGENT_TO_MANAGER = 2
    MANAGER_TO_USER = 3
    EMERGENCY = 4


class SeverityLevel(int, Enum):
    INFORMATIONAL = 1
    WARNING = 2
    SIGNIFICANT_RISK = 3
    CRITICAL = 4
    EMERGENCY = 5


SEVERITY_TO_LEVEL: Dict[SeverityLevel, EscalationLevel] = {
    SeverityLevel.INFORMATIONAL: EscalationLevel.AGENT_TO_AGENT,
    SeverityLevel.WARNING: EscalationLevel.AGENT_TO_MANAGER,
    SeverityLevel.SIGNIFICANT_RISK: EscalationLevel.AGENT_TO_MANAGER,
    SeverityLevel.CRITICAL: EscalationLevel.MANAGER_TO_USER,
    SeverityLevel.EMERGENCY: EscalationLevel.EMERGENCY,
}


EMERGENCY_OUTCOMES = ["continue", "pause", "rollback", "replan", "user_escalation"]


@dataclass
class EscalationPackage:
    issue: str
    severity: SeverityLevel
    impact: str
    evidence: List[str]
    recommendations: List[str]
    confidence: str
    proposed_action: str
    source_agent: str
    target_agent: str = "manager"
    escalation_level: EscalationLevel = EscalationLevel.AGENT_TO_MANAGER
    status: str = "open"
    resolution: str = ""
    outcome: str = ""
    correlation_id: Optional[str] = None
    timestamp: str = ""
    escalation_id: str = ""


class EscalationManager:
    def __init__(self):
        self._escalations: List[EscalationPackage] = []

    def escalate(self, issue: str, severity: SeverityLevel, impact: str,
                 source_agent: str, evidence: Optional[List[str]] = None,
                 recommendations: Optional[List[str]] = None,
                 confidence: str = "medium",
                 proposed_action: str = "",
                 target_agent: str = "manager",
                 correlation_id: Optional[str] = None) -> EscalationPackage:
        level = SEVERITY_TO_LEVEL.get(severity, EscalationLevel.AGENT_TO_MANAGER)
        pkg = EscalationPackage(
            escalation_id=f"esc-{len(self._escalations) + 1}",
            issue=issue,
            severity=severity,
            impact=impact,
            evidence=evidence or [],
            recommendations=recommendations or [],
            confidence=confidence,
            proposed_action=proposed_action,
            source_agent=source_agent,
            target_agent=target_agent,
            escalation_level=level,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow().isoformat(),
        )

        if level == EscalationLevel.EMERGENCY:
            target_agent = "architect"

        self._escalations.append(pkg)

        decision_trace.record(
            task=f"escalation: {issue[:80]}",
            reason=f"Level {level.value} escalation from {source_agent}: {issue[:120]}",
            evidence=evidence or [],
            confidence=confidence,
            owner=source_agent,
            impact={"severity": severity.value, "level": level.value, "impact": impact},
            source="escalation_manager",
            correlation_id=correlation_id,
        )

        priority = EventPriority.CRITICAL if level == EscalationLevel.EMERGENCY else (
            EventPriority.HIGH if level == EscalationLevel.MANAGER_TO_USER else
            EventPriority.NORMAL
        )
        event_bus.publish(Event(
            topic="escalation.created",
            source="escalation_manager",
            data={
                "escalation_id": pkg.escalation_id,
                "level": level.value,
                "severity": severity.value,
                "issue": issue[:100],
                "source_agent": source_agent,
                "target": target_agent,
                "confidence": confidence,
            },
            priority=priority,
            correlation_id=correlation_id,
        ))
        return pkg

    def resolve(self, escalation_id: str, resolution: str, outcome: str):
        for pkg in self._escalations:
            if pkg.escalation_id == escalation_id:
                pkg.status = "resolved"
                pkg.resolution = resolution
                pkg.outcome = outcome
                return pkg
        return None

    def emergency_pause(self, reason: str, source_agent: str,
                        correlation_id: Optional[str] = None) -> EscalationPackage:
        return self.escalate(
            issue=f"EMERGENCY PAUSE: {reason}",
            severity=SeverityLevel.EMERGENCY,
            impact="Execution paused pending resolution",
            source_agent=source_agent,
            evidence=["Emergency protocol triggered"],
            recommendations=["Evaluate pause conditions", "Determine next action"],
            confidence="high",
            proposed_action="pause",
            target_agent="architect",
            correlation_id=correlation_id,
        )

    def emergency_rollback(self, reason: str, source_agent: str,
                           correlation_id: Optional[str] = None) -> EscalationPackage:
        return self.escalate(
            issue=f"EMERGENCY ROLLBACK: {reason}",
            severity=SeverityLevel.EMERGENCY,
            impact="System rollback required",
            source_agent=source_agent,
            evidence=["Rollback protocol triggered"],
            recommendations=["Identify rollback point", "Execute rollback", "Verify state"],
            confidence="high",
            proposed_action="rollback",
            target_agent="architect",
            correlation_id=correlation_id,
        )

    def security_escalation(self, issue: str, source_agent: str,
                            evidence: Optional[List[str]] = None,
                            correlation_id: Optional[str] = None) -> EscalationPackage:
        return self.escalate(
            issue=issue,
            severity=SeverityLevel.CRITICAL,
            impact="Security integrity at risk",
            source_agent=source_agent,
            evidence=evidence or ["Security violation detected"],
            recommendations=["Contain threat", "Assess impact", "Notify user"],
            confidence="high",
            proposed_action="immediate_review",
            target_agent="manager",
            correlation_id=correlation_id,
        )

    def get(self, escalation_id: str) -> Optional[EscalationPackage]:
        for pkg in self._escalations:
            if pkg.escalation_id == escalation_id:
                return pkg
        return None

    def find(self, source_agent: Optional[str] = None,
             severity: Optional[SeverityLevel] = None,
             status: Optional[str] = None,
             limit: int = 50) -> List[EscalationPackage]:
        results = list(reversed(self._escalations))
        if source_agent:
            results = [e for e in results if e.source_agent == source_agent]
        if severity:
            results = [e for e in results if e.severity == severity]
        if status:
            results = [e for e in results if e.status == status]
        return results[:limit]

    def summary(self) -> Dict[str, Any]:
        by_severity = {}
        by_status = {}
        by_agent = {}
        for e in self._escalations:
            by_severity[e.severity.name] = by_severity.get(e.severity.name, 0) + 1
            by_status[e.status] = by_status.get(e.status, 0) + 1
            by_agent[e.source_agent] = by_agent.get(e.source_agent, 0) + 1
        return {
            "total": len(self._escalations),
            "by_severity": by_severity,
            "by_status": by_status,
            "by_agent": by_agent,
        }


escalation_manager = EscalationManager()
