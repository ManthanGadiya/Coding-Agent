from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field

from backend.decision_runtime.event_bus import event_bus, Event, EventPriority
from backend.decision_runtime.registries import workflow_registry, WorkflowDef, WorkflowStep
from backend.decision_runtime.logger import decision_logger, LogLevel


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class StepResult:
    step_name: str
    status: ExecutionStatus
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


StepHandler = Callable[[WorkflowStep, Dict[str, Any]], Dict[str, Any]]


class WorkflowExecutor:
    def __init__(self):
        self._handlers: Dict[str, StepHandler] = {}
        self._instances: Dict[str, Dict[str, Any]] = {}

    def register_handler(self, step_type: str, handler: StepHandler):
        self._handlers[step_type] = handler

    def execute(self, workflow_name: str, context: Optional[Dict] = None,
                instance_id: Optional[str] = None) -> Dict[str, Any]:
        workflow = workflow_registry.get(workflow_name)
        if not workflow:
            return {"error": f"Workflow '{workflow_name}' not found", "status": "failed"}

        instance_id = instance_id or f"wf-inst-{id(workflow)}"
        state: Dict[str, Any] = {
            "workflow_name": workflow_name,
            "instance_id": instance_id,
            "status": ExecutionStatus.RUNNING,
            "context": context or {},
            "step_results": [],
            "current_step": 0,
        }
        self._instances[instance_id] = state

        decision_logger.info(f"workflow.start", f"Starting workflow '{workflow_name}'",
                             source="workflow_executor", data={"instance_id": instance_id})

        event_bus.publish(Event(
            topic="workflow.started",
            source="workflow_executor",
            data={"workflow_name": workflow_name, "instance_id": instance_id},
            priority=EventPriority.NORMAL,
        ))

        for i, step in enumerate(workflow.steps):
            state["current_step"] = i
            handler = self._handlers.get(step.type)
            if not handler:
                state["status"] = ExecutionStatus.FAILED
                return {"error": f"No handler for step type '{step.type}'",
                        "instance_id": instance_id, "status": "failed"}

            try:
                step_context = {**state["context"], **step.config}
                output = handler(step, step_context)
                step_result = StepResult(
                    step_name=step.name,
                    status=ExecutionStatus.COMPLETED,
                    output=output,
                )
                state["step_results"].append(step_result)
                state["context"].update(output)

                decision_logger.info(f"workflow.step_complete", f"Step '{step.name}' complete",
                                     source="workflow_executor",
                                     data={"step": step.name, "instance_id": instance_id})
            except Exception as e:
                step_result = StepResult(
                    step_name=step.name,
                    status=ExecutionStatus.FAILED,
                    error=str(e),
                )
                state["step_results"].append(step_result)
                state["status"] = ExecutionStatus.FAILED

                decision_logger.error(f"workflow.step_failed", f"Step '{step.name}' failed: {e}",
                                      source="workflow_executor",
                                      data={"step": step.name, "error": str(e)})
                event_bus.publish(Event(
                    topic="workflow.failed",
                    source="workflow_executor",
                    data={"workflow_name": workflow_name, "instance_id": instance_id,
                          "step": step.name, "error": str(e)},
                    priority=EventPriority.HIGH,
                ))
                return {"error": str(e), "instance_id": instance_id, "status": "failed"}

        state["status"] = ExecutionStatus.COMPLETED

        event_bus.publish(Event(
            topic="workflow.completed",
            source="workflow_executor",
            data={"workflow_name": workflow_name, "instance_id": instance_id,
                  "steps_completed": len(workflow.steps)},
            priority=EventPriority.NORMAL,
        ))

        return {
            "instance_id": instance_id,
            "status": "completed",
            "steps": [{"name": r.step_name, "status": r.status.value} for r in state["step_results"]],
            "result": state["context"],
        }

    def pause(self, instance_id: str) -> bool:
        state = self._instances.get(instance_id)
        if not state or state["status"] != ExecutionStatus.RUNNING:
            return False
        state["status"] = ExecutionStatus.PAUSED
        return True

    def resume(self, instance_id: str) -> bool:
        state = self._instances.get(instance_id)
        if not state or state["status"] != ExecutionStatus.PAUSED:
            return False
        state["status"] = ExecutionStatus.RUNNING
        return True

    def cancel(self, instance_id: str) -> bool:
        state = self._instances.get(instance_id)
        if not state:
            return False
        state["status"] = ExecutionStatus.CANCELLED
        return True

    def get_state(self, instance_id: str) -> Optional[Dict[str, Any]]:
        return self._instances.get(instance_id)


workflow_executor = WorkflowExecutor()
