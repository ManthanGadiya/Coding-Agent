from typing import Any, Dict, List, Optional
from datetime import datetime

from backend.decision_runtime.event_bus import event_bus, Event, EventPriority


class MemoryHooks:
    def before_execution(self, task_type: str, agent: str, context: Optional[Dict] = None) -> Dict:
        record = {
            "event": "execution_start",
            "task_type": task_type,
            "agent": agent,
            "timestamp": datetime.utcnow().isoformat(),
            "context_snapshot": context or {},
        }
        event_bus.publish(Event(
            topic="memory.execution_start",
            source="memory_hooks",
            data=record,
            priority=EventPriority.LOW,
            correlation_id=(context or {}).get("correlation_id"),
        ))
        return record

    def after_execution(self, task_type: str, agent: str, result: Dict,
                         context: Optional[Dict] = None) -> Dict:
        record = {
            "event": "execution_complete",
            "task_type": task_type,
            "agent": agent,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
        event_bus.publish(Event(
            topic="memory.execution_complete",
            source="memory_hooks",
            data=record,
            priority=EventPriority.LOW,
            correlation_id=(context or {}).get("correlation_id"),
        ))
        return record

    def record_decision(self, decision: Dict) -> Dict:
        record = {
            "event": "decision_recorded",
            "decision": decision,
            "timestamp": datetime.utcnow().isoformat(),
        }
        event_bus.publish(Event(
            topic="memory.decision_recorded",
            source="memory_hooks",
            data=record,
            priority=EventPriority.LOW,
            correlation_id=decision.get("correlation_id"),
        ))
        return record

    def record_error(self, error: str, context: Optional[Dict] = None) -> Dict:
        record = {
            "event": "error_recorded",
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
        }
        event_bus.publish(Event(
            topic="memory.error_recorded",
            source="memory_hooks",
            data=record,
            priority=EventPriority.HIGH,
            correlation_id=(context or {}).get("correlation_id"),
        ))
        return record


memory_hooks = MemoryHooks()
