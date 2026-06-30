from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from backend.decision_runtime.event_bus import event_bus, Event, EventPriority
from backend.decision_runtime.environment_mode import mode_controller


@dataclass
class TraceRecord:
    decision_id: str
    task: str
    reason: str
    evidence: List[str]
    confidence: str
    owner: str = "runtime"
    impact: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    outcome: str = ""
    storage_location: str = ""
    timestamp: str = ""
    correlation_id: Optional[str] = None


class DecisionTrace:
    def __init__(self):
        self._traces: List[TraceRecord] = []

    def record(self, task: str, reason: str, evidence: Optional[List[str]] = None,
               confidence: str = "medium", owner: str = "runtime",
               impact: Optional[Dict] = None, source: str = "decision_engine",
               correlation_id: Optional[str] = None) -> TraceRecord:
        trace = TraceRecord(
            decision_id=f"tr-{len(self._traces) + 1}",
            task=task,
            reason=reason,
            evidence=evidence or [],
            confidence=confidence,
            owner=owner,
            impact=impact or {},
            source=source,
            timestamp=datetime.utcnow().isoformat(),
            correlation_id=correlation_id,
        )
        self._traces.append(trace)

        event_bus.publish(Event(
            topic="trace.recorded",
            source="decision_trace",
            data={
                "decision_id": trace.decision_id,
                "task": task[:100],
                "reason": reason[:200],
                "evidence_count": len(trace.evidence),
                "confidence": confidence,
                "owner": owner,
            },
            priority=EventPriority.LOW,
            correlation_id=correlation_id,
        ))
        return trace

    def resolve(self, decision_id: str, outcome: str,
                storage_location: str = "") -> Optional[TraceRecord]:
        for trace in self._traces:
            if trace.decision_id == decision_id:
                trace.outcome = outcome
                trace.storage_location = storage_location
                return trace
        return None

    def get(self, decision_id: str) -> Optional[TraceRecord]:
        for trace in self._traces:
            if trace.decision_id == decision_id:
                return trace
        return None

    def find(self, task: Optional[str] = None, owner: Optional[str] = None,
             confidence: Optional[str] = None, limit: int = 50) -> List[TraceRecord]:
        results = list(self._traces)
        if task:
            results = [t for t in results if task.lower() in t.task.lower()]
        if owner:
            results = [t for t in results if t.owner == owner]
        if confidence:
            results = [t for t in results if t.confidence == confidence]
        return results[-limit:]

    def summary(self) -> Dict[str, Any]:
        by_confidence = {}
        by_owner = {}
        for t in self._traces:
            by_confidence[t.confidence] = by_confidence.get(t.confidence, 0) + 1
            by_owner[t.owner] = by_owner.get(t.owner, 0) + 1
        return {
            "total_decisions": len(self._traces),
            "by_confidence": by_confidence,
            "by_owner": by_owner,
        }


decision_trace = DecisionTrace()
