from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from backend.decision_runtime.event_bus import event_bus, Event, EventPriority


class RuntimeState(str, Enum):
    RECEIVED = "received"
    CLASSIFYING = "classifying"
    MEMORY_LOADING = "memory_loading"
    CORE_DECISION = "core_decision"
    AGENT_SELECTION = "agent_selection"
    SKILL_SELECTION = "skill_selection"
    MCP_SELECTION = "mcp_selection"
    MODEL_SELECTION = "model_selection"
    APPROVAL_CHECK = "approval_check"
    RESEARCHING = "researching"
    ARCHITECTING = "architecting"
    PLANNING = "planning"
    APPROVING = "approving"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REVIEWING = "reviewing"
    DOCUMENTING = "documenting"
    VALIDATING = "validating"
    MEMORY_UPDATING = "memory_updating"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


TRANSITIONS: Dict[RuntimeState, List[RuntimeState]] = {
    RuntimeState.RECEIVED: [RuntimeState.CLASSIFYING],
    RuntimeState.CLASSIFYING: [RuntimeState.MEMORY_LOADING],
    RuntimeState.MEMORY_LOADING: [RuntimeState.CORE_DECISION, RuntimeState.FAILED],
    RuntimeState.CORE_DECISION: [RuntimeState.AGENT_SELECTION, RuntimeState.FAILED],
    RuntimeState.AGENT_SELECTION: [RuntimeState.SKILL_SELECTION],
    RuntimeState.SKILL_SELECTION: [RuntimeState.MCP_SELECTION],
    RuntimeState.MCP_SELECTION: [RuntimeState.MODEL_SELECTION],
    RuntimeState.MODEL_SELECTION: [RuntimeState.APPROVAL_CHECK],
    RuntimeState.APPROVAL_CHECK: [RuntimeState.RESEARCHING, RuntimeState.BLOCKED, RuntimeState.ESCALATED],
    RuntimeState.RESEARCHING: [RuntimeState.ARCHITECTING, RuntimeState.DEBUGGING],
    RuntimeState.ARCHITECTING: [RuntimeState.PLANNING],
    RuntimeState.PLANNING: [RuntimeState.APPROVING],
    RuntimeState.APPROVING: [RuntimeState.IMPLEMENTING, RuntimeState.BLOCKED],
    RuntimeState.IMPLEMENTING: [RuntimeState.TESTING],
    RuntimeState.TESTING: [RuntimeState.DEBUGGING, RuntimeState.REVIEWING],
    RuntimeState.DEBUGGING: [RuntimeState.IMPLEMENTING, RuntimeState.FAILED],
    RuntimeState.REVIEWING: [RuntimeState.DOCUMENTING, RuntimeState.IMPLEMENTING],
    RuntimeState.DOCUMENTING: [RuntimeState.VALIDATING],
    RuntimeState.VALIDATING: [RuntimeState.MEMORY_UPDATING, RuntimeState.FAILED, RuntimeState.BLOCKED],
    RuntimeState.MEMORY_UPDATING: [RuntimeState.COMPLETED, RuntimeState.FAILED],
    RuntimeState.BLOCKED: [RuntimeState.RECEIVED, RuntimeState.ESCALATED, RuntimeState.CANCELLED],
    RuntimeState.ESCALATED: [RuntimeState.RECEIVED, RuntimeState.CANCELLED],
    RuntimeState.FAILED: [RuntimeState.RECEIVED, RuntimeState.CANCELLED],
    RuntimeState.CANCELLED: [],
    RuntimeState.COMPLETED: [],
}


@dataclass
class StateTransition:
    from_state: RuntimeState
    to_state: RuntimeState
    timestamp: str = ""
    reason: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class StateMachineInstance:
    instance_id: str
    current_state: RuntimeState = RuntimeState.RECEIVED
    transitions: List[StateTransition] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    completed_at: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            now = datetime.utcnow().isoformat()
            self.created_at = now
            self.updated_at = now


class StateMachine:
    def __init__(self):
        self._instances: Dict[str, StateMachineInstance] = {}

    def create(self, instance_id: str, context: Optional[Dict] = None) -> StateMachineInstance:
        instance = StateMachineInstance(
            instance_id=instance_id,
            context=context or {},
        )
        self._instances[instance_id] = instance
        event_bus.publish(Event(
            topic="state_machine.created",
            source="state_machine",
            data={"instance_id": instance_id, "state": instance.current_state.value},
            correlation_id=instance_id,
        ))
        return instance

    def transition(self, instance_id: str, to_state: RuntimeState, reason: str = "",
                    data: Optional[Dict] = None) -> Optional[StateMachineInstance]:
        instance = self._instances.get(instance_id)
        if not instance:
            return None

        if to_state not in TRANSITIONS.get(instance.current_state, []):
            allowed = [s.value for s in TRANSITIONS.get(instance.current_state, [])]
            raise ValueError(
                f"Cannot transition from {instance.current_state.value} to {to_state.value}. "
                f"Allowed: {allowed}"
            )

        transition = StateTransition(
            from_state=instance.current_state,
            to_state=to_state,
            reason=reason,
            data=data or {},
        )
        instance.transitions.append(transition)
        instance.current_state = to_state
        instance.updated_at = datetime.utcnow().isoformat()

        if to_state in (RuntimeState.COMPLETED, RuntimeState.FAILED, RuntimeState.CANCELLED):
            instance.completed_at = datetime.utcnow().isoformat()

        event_bus.publish(Event(
            topic=f"state_machine.{to_state.value}",
            source="state_machine",
            data={
                "instance_id": instance_id,
                "from_state": transition.from_state.value,
                "to_state": to_state.value,
                "reason": reason,
            },
            correlation_id=instance_id,
        ))
        return instance

    def get(self, instance_id: str) -> Optional[StateMachineInstance]:
        return self._instances.get(instance_id)

    def can_transition(self, instance_id: str, to_state: RuntimeState) -> bool:
        instance = self._instances.get(instance_id)
        if not instance:
            return False
        return to_state in TRANSITIONS.get(instance.current_state, [])

    def get_state(self, instance_id: str) -> Optional[RuntimeState]:
        instance = self._instances.get(instance_id)
        return instance.current_state if instance else None

    def list_active(self) -> List[StateMachineInstance]:
        terminal = {RuntimeState.COMPLETED, RuntimeState.FAILED, RuntimeState.CANCELLED}
        return [i for i in self._instances.values() if i.current_state not in terminal]

    def remove(self, instance_id: str):
        self._instances.pop(instance_id, None)


state_machine = StateMachine()
