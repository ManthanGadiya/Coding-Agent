from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field

from backend.decision_runtime.event_bus import event_bus, Event, EventPriority


class ConflictSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConflictStep(str, Enum):
    IDENTIFIED = "identified"
    DIRECT_DISCUSSION = "direct_discussion"
    EVIDENCE_EXCHANGE = "evidence_exchange"
    CONSENSUS_ATTEMPT = "consensus_attempt"
    MANAGER_ARBITRATION = "manager_arbitration"
    USER_ESCALATION = "user_escalation"


@dataclass
class ConflictRecord:
    conflict_id: str
    issue: str
    agents_involved: List[str]
    severity: ConflictSeverity
    arguments: Dict[str, str] = field(default_factory=dict)
    evidence: Dict[str, List[str]] = field(default_factory=dict)
    current_step: ConflictStep = ConflictStep.IDENTIFIED
    resolution: Optional[str] = None
    outcome: Optional[str] = None
    reasoning: Optional[str] = None
    created_at: str = ""
    resolved_at: Optional[str] = None


CONFLICT_PATHS: Dict[Tuple[str, str], str] = {
    ("planner", "architect"): "Planner may challenge architecture with evidence",
    ("coder", "architect"): "Coder may challenge architecture when implementation is difficult",
    ("tester", "coder"): "Tester may block completion on failed tests",
    ("reviewer", "coder"): "Reviewer may reject unsafe or low-quality code",
    ("reviewer", "architect"): "Reviewer may challenge architecture on security grounds",
    ("debugger", "coder"): "Debugger may reject fixes that miss root cause",
    ("memory", "*"): "Memory Agent cannot block execution but may recommend",
}


class ConflictResolver:
    def __init__(self):
        self._records: List[ConflictRecord] = []

    def resolve(self, agents: List[str], issue: str, arguments: Dict[str, str],
                 evidence: Optional[Dict[str, List[str]]] = None,
                 severity: str = "medium") -> Dict[str, Any]:
        record = ConflictRecord(
            conflict_id=f"cf-{len(self._records) + 1}",
            issue=issue,
            agents_involved=agents,
            severity=ConflictSeverity(severity),
            arguments=arguments,
            evidence=evidence or {},
            created_at=datetime.utcnow().isoformat(),
        )

        path = CONFLICT_PATHS.get((agents[0], agents[1])) if len(agents) >= 2 else None
        if not path and len(agents) >= 2:
            path = CONFLICT_PATHS.get((agents[0], "*"))
        record.current_step = ConflictStep.DIRECT_DISCUSSION

        scores = self._score_arguments(agents, arguments, evidence or {})
        if self._try_consensus(scores):
            record.current_step = ConflictStep.CONSENSUS_ATTEMPT
            record.resolution = "consensus"
            record.reasoning = "Agents reached consensus through evidence exchange"
            record.outcome = "resolved"
        else:
            record.current_step = ConflictStep.MANAGER_ARBITRATION
            winner = self._arbitrate(agents, scores)
            record.resolution = winner
            record.reasoning = self._build_arbitration_reasoning(agents, scores, winner)
            record.outcome = "resolved"

            if severity in ("high", "critical"):
                record.current_step = ConflictStep.USER_ESCALATION
                record.outcome = "escalated_to_user"

        record.resolved_at = datetime.utcnow().isoformat()
        self._records.append(record)

        event_bus.publish(Event(
            topic="conflict.resolved",
            source="conflict_resolver",
            data={
                "conflict_id": record.conflict_id,
                "issue": issue,
                "agents": agents,
                "resolution": record.resolution,
                "outcome": record.outcome,
                "severity": severity,
            },
            priority=EventPriority.HIGH if severity in ("high", "critical") else EventPriority.NORMAL,
        ))

        return {
            "conflict_id": record.conflict_id,
            "issue": issue,
            "agents": agents,
            "resolution": record.resolution,
            "outcome": record.outcome,
            "step": record.current_step.value,
            "reasoning": record.reasoning,
            "severity": severity,
        }

    def _score_arguments(self, agents: List[str], arguments: Dict[str, str],
                          evidence: Dict[str, List[str]]) -> Dict[str, float]:
        scores = {}
        for agent in agents:
            arg = arguments.get(agent, "")
            ev = evidence.get(agent, [])
            arg_score = min(len(arg) / 300, 1.0)
            ev_score = min(len(ev) * 0.25, 1.0)
            scores[agent] = round(arg_score * 0.4 + ev_score * 0.6, 3)
        return scores

    def _try_consensus(self, scores: Dict[str, float]) -> bool:
        if len(scores) < 2:
            return True
        values = list(scores.values())
        max_v, min_v = max(values), min(values)
        if max_v == 0:
            return True
        return (max_v - min_v) / max_v < 0.2

    def _arbitrate(self, agents: List[str], scores: Dict[str, float]) -> str:
        return max(agents, key=lambda a: scores.get(a, 0))

    def _build_arbitration_reasoning(self, agents: List[str], scores: Dict[str, float],
                                      winner: str) -> str:
        parts = [f"Manager arbitration:"]
        for agent in agents:
            parts.append(f"{agent}={scores.get(agent, 0):.3f}")
        parts.append(f"→ {winner} wins")
        return " ".join(parts)

    def get_history(self, limit: int = 50) -> List[ConflictRecord]:
        return self._records[-limit:]


conflict_resolver = ConflictResolver()
