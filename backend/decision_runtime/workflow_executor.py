from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import asyncio

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


class ErrorStrategy(str, Enum):
    ABORT = "abort"
    SKIP = "skip"
    RETRY = "retry"


@dataclass
class StepResult:
    step_name: str
    status: ExecutionStatus
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    attempts: int = 1


StepHandler = Callable[[WorkflowStep, Dict[str, Any]], Dict[str, Any]]


class WorkflowExecutor:
    def __init__(self):
        self._handlers: Dict[str, StepHandler] = {}
        self._instances: Dict[str, Dict[str, Any]] = {}
        self._default_max_retries = 2

    def register_handler(self, step_type: str, handler: StepHandler):
        self._handlers[step_type] = handler

    def _should_stop(self, state: Dict) -> bool:
        return state["status"] in (ExecutionStatus.PAUSED, ExecutionStatus.CANCELLED)

    async def execute_async(self, workflow_name: str, context: Optional[Dict] = None,
                            instance_id: Optional[str] = None) -> Dict[str, Any]:
        workflow = workflow_registry.get(workflow_name)
        if not workflow:
            return {"error": f"Workflow '{workflow_name}' not found", "status": "failed"}

        instance_id = instance_id or f"wf-{workflow_name}-{id(workflow)}"
        max_retries = getattr(workflow, "max_retries", self._default_max_retries)
        error_strategy = getattr(workflow, "error_strategy", ErrorStrategy.ABORT)

        state: Dict[str, Any] = {
            "workflow_name": workflow_name,
            "instance_id": instance_id,
            "status": ExecutionStatus.RUNNING,
            "context": context or {},
            "step_results": [],
            "current_step": 0,
            "max_retries": max_retries,
            "error_strategy": error_strategy,
        }
        self._instances[instance_id] = state

        decision_logger.info("workflow.start", f"Starting workflow '{workflow_name}'",
                             source="workflow_executor", data={"instance_id": instance_id})
        event_bus.publish(Event(topic="workflow.started", source="workflow_executor",
                                data={"workflow_name": workflow_name, "instance_id": instance_id},
                                priority=EventPriority.NORMAL))

        for i, step in enumerate(workflow.steps):
            if self._should_stop(state):
                break
            state["current_step"] = i
            handler = self._handlers.get(step.type)
            if not handler:
                state["status"] = ExecutionStatus.FAILED
                return {"error": f"No handler for step type '{step.type}'",
                        "instance_id": instance_id, "status": "failed"}

            result = await self._execute_step(step, handler, state, max_retries, error_strategy)
            state["step_results"].append(result)

            if result.status == ExecutionStatus.FAILED:
                if error_strategy == ErrorStrategy.ABORT:
                    state["status"] = ExecutionStatus.FAILED
                    return {"error": result.error, "instance_id": instance_id, "status": "failed",
                            "step": step.name}
                continue

            if self._should_stop(state):
                break

        if state["status"] == ExecutionStatus.RUNNING:
            state["status"] = ExecutionStatus.COMPLETED
            event_bus.publish(Event(topic="workflow.completed", source="workflow_executor",
                                    data={"workflow_name": workflow_name, "instance_id": instance_id},
                                    priority=EventPriority.NORMAL))

        return {
            "instance_id": instance_id,
            "status": state["status"].value,
            "steps": [{"name": r.step_name, "status": r.status.value, "attempts": r.attempts,
                       "error": r.error} for r in state["step_results"]],
            "result": state["context"],
        }

    async def _execute_step(self, step: WorkflowStep, handler: StepHandler,
                             state: Dict, max_retries: int,
                             error_strategy: ErrorStrategy) -> StepResult:
        step_context = {**state["context"], **step.config}

        for attempt in range(1, max_retries + 2):
            if self._should_stop(state):
                return StepResult(step_name=step.name, status=ExecutionStatus.CANCELLED)

            try:
                output = handler(step, step_context)
                if asyncio.iscoroutine(output):
                    output = await output
                result = StepResult(step_name=step.name, status=ExecutionStatus.COMPLETED,
                                    output=output, attempts=attempt)
                state["context"].update(output)
                decision_logger.info("workflow.step_complete", f"Step '{step.name}' complete",
                                     source="workflow_executor",
                                     data={"step": step.name, "attempt": attempt})
                return result
            except Exception as e:
                decision_logger.warning("workflow.step_retry", f"Step '{step.name}' failed (attempt {attempt}): {e}",
                                        source="workflow_executor",
                                        data={"step": step.name, "attempt": attempt})

                if attempt > max_retries and error_strategy == ErrorStrategy.ABORT:
                    event_bus.publish(Event(topic="workflow.failed", source="workflow_executor",
                                            data={"workflow_name": state["workflow_name"],
                                                  "instance_id": state["instance_id"],
                                                  "step": step.name, "error": str(e)},
                                            priority=EventPriority.HIGH))
                    return StepResult(step_name=step.name, status=ExecutionStatus.FAILED,
                                      error=str(e), attempts=attempt)

        return StepResult(step_name=step.name, status=ExecutionStatus.FAILED,
                          error="Max retries exceeded", attempts=max_retries + 1)

    def execute(self, workflow_name: str, context: Optional[Dict] = None,
                instance_id: Optional[str] = None) -> Dict[str, Any]:
        workflow = workflow_registry.get(workflow_name)
        if not workflow:
            return {"error": f"Workflow '{workflow_name}' not found", "status": "failed"}

        instance_id = instance_id or f"wf-{workflow_name}-{id(workflow)}"
        state: Dict[str, Any] = {
            "workflow_name": workflow_name,
            "instance_id": instance_id,
            "status": ExecutionStatus.RUNNING,
            "context": context or {},
            "step_results": [],
            "current_step": 0,
        }
        self._instances[instance_id] = state
        decision_logger.info("workflow.start", f"Starting workflow '{workflow_name}'",
                             source="workflow_executor", data={"instance_id": instance_id})
        event_bus.publish(Event(topic="workflow.started", source="workflow_executor",
                                data={"workflow_name": workflow_name, "instance_id": instance_id},
                                priority=EventPriority.NORMAL))

        max_retries = self._default_max_retries

        for i, step in enumerate(workflow.steps):
            if state["status"] == ExecutionStatus.CANCELLED:
                break
            state["current_step"] = i
            handler = self._handlers.get(step.type)
            if not handler:
                state["status"] = ExecutionStatus.FAILED
                return {"error": f"No handler for step type '{step.type}'",
                        "instance_id": instance_id, "status": "failed"}

            step_context = {**state["context"], **step.config}
            step_ok = False
            step_error = None
            attempts = 0

            for attempt in range(1, max_retries + 2):
                attempts = attempt
                try:
                    output = handler(step, step_context)
                    state["step_results"].append(StepResult(step_name=step.name,
                        status=ExecutionStatus.COMPLETED, output=output, attempts=attempt))
                    state["context"].update(output)
                    step_ok = True
                    break
                except Exception as e:
                    step_error = str(e)
                    decision_logger.warning("workflow.step_retry",
                        f"Step '{step.name}' failed (attempt {attempt}): {e}",
                        source="workflow_executor",
                        data={"step": step.name, "attempt": attempt})

            if not step_ok:
                state["step_results"].append(StepResult(step_name=step.name,
                    status=ExecutionStatus.FAILED, error=step_error, attempts=attempts))
                state["status"] = ExecutionStatus.FAILED
                event_bus.publish(Event(topic="workflow.failed", source="workflow_executor",
                    data={"workflow_name": workflow_name, "instance_id": instance_id,
                          "step": step.name, "error": step_error}, priority=EventPriority.HIGH))
                return {"error": step_error, "instance_id": instance_id,
                        "status": "failed", "step": step.name}

        if state["status"] != ExecutionStatus.CANCELLED:
            state["status"] = ExecutionStatus.COMPLETED
            event_bus.publish(Event(topic="workflow.completed", source="workflow_executor",
                data={"workflow_name": workflow_name, "instance_id": instance_id},
                priority=EventPriority.NORMAL))

        return {
            "instance_id": instance_id,
            "status": state["status"].value,
            "steps": [{"name": r.step_name, "status": r.status.value}
                      for r in state["step_results"]],
            "result": state["context"],
        }

    def pause(self, instance_id: str) -> bool:
        state = self._instances.get(instance_id)
        if not state or state["status"] not in (ExecutionStatus.RUNNING, ExecutionStatus.PENDING):
            return False
        state["status"] = ExecutionStatus.PAUSED
        decision_logger.info("workflow.paused", f"Workflow '{instance_id}' paused",
                             source="workflow_executor")
        return True

    def resume(self, instance_id: str) -> bool:
        state = self._instances.get(instance_id)
        if not state or state["status"] != ExecutionStatus.PAUSED:
            return False
        state["status"] = ExecutionStatus.RUNNING
        decision_logger.info("workflow.resumed", f"Workflow '{instance_id}' resumed",
                             source="workflow_executor")
        return True

    def cancel(self, instance_id: str) -> bool:
        state = self._instances.get(instance_id)
        if not state:
            return False
        state["status"] = ExecutionStatus.CANCELLED
        decision_logger.info("workflow.cancelled", f"Workflow '{instance_id}' cancelled",
                             source="workflow_executor")
        return True

    def get_state(self, instance_id: str) -> Optional[Dict[str, Any]]:
        return self._instances.get(instance_id)

    def list_instances(self, status: Optional[str] = None) -> List[Dict]:
        result = []
        for inst_id, state in self._instances.items():
            if status and state["status"].value != status:
                continue
            result.append({
                "instance_id": inst_id,
                "workflow_name": state["workflow_name"],
                "status": state["status"].value,
                "current_step": state["current_step"],
                "steps_completed": len(state.get("step_results", [])),
            })
        return result


workflow_executor = WorkflowExecutor()
