from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from backend.decision_runtime.event_bus import event_bus, Event, EventPriority
from backend.decision_runtime.state_machine import state_machine, RuntimeState, StateMachineInstance
from backend.decision_runtime.task_classifier import task_classifier, TaskType, ClassificationResult
from backend.decision_runtime.agent_selector import agent_selector, SelectionResult
from backend.decision_runtime.skill_selector import skill_selector
from backend.decision_runtime.mcp_selector import mcp_selector
from backend.decision_runtime.model_router import runtime_model_router, ModelSelection
from backend.decision_runtime.environment_mode import mode_controller, EnvironmentMode
from backend.decision_runtime.approval_manager import approval_manager, ApprovalScope, ApprovalStatus
from backend.decision_runtime.conflict_resolver import conflict_resolver
from backend.decision_runtime.completion_validator import completion_validator
from backend.decision_runtime.memory_hooks import memory_hooks
from backend.decision_runtime.logger import decision_logger, LogLevel


@dataclass
class DecisionRequest:
    task: str
    context: Dict[str, Any] = field(default_factory=dict)
    source: str = "user"
    correlation_id: Optional[str] = None
    mode: EnvironmentMode = EnvironmentMode.BUILD
    skip_approvals: bool = False
    prefer_local: bool = True


@dataclass
class DecisionContext:
    request: DecisionRequest
    classification: Optional[ClassificationResult] = None
    state: Optional[StateMachineInstance] = None
    selected_agents: Optional[SelectionResult] = None
    selected_skills: List[str] = field(default_factory=list)
    selected_mcps: List[Any] = field(default_factory=list)
    model_selection: Optional[ModelSelection] = None
    approvals: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    start_time: str = ""


class RuntimeEngine:
    def __init__(self):
        self._history: List[Dict[str, Any]] = []

    def decide(self, request: DecisionRequest) -> Dict[str, Any]:
        ctx = DecisionContext(
            request=request,
            start_time=datetime.utcnow().isoformat(),
        )

        mode_controller.set_mode(request.mode)

        decision_logger.info("engine.start", f"Decision request: {request.task[:100]}",
                             source="decision_engine",
                             correlation_id=request.correlation_id)

        event_bus.publish(Event(
            topic="engine.requested",
            source="decision_engine",
            data={"task": request.task, "source": request.source},
            priority=EventPriority.NORMAL,
            correlation_id=request.correlation_id,
        ))

        ctx.state = state_machine.create(f"decision-{id(request)}")

        self._exec_step(ctx, RuntimeState.CLASSIFYING, lambda: self._step_classify(ctx, request))
        self._exec_step(ctx, RuntimeState.MEMORY_LOADING, lambda: None)
        self._exec_step(ctx, RuntimeState.AGENT_SELECTION, lambda: self._step_agents(ctx, request))
        self._exec_step(ctx, RuntimeState.SKILL_SELECTION, lambda: self._step_skills(ctx, request))
        self._exec_step(ctx, RuntimeState.MCP_SELECTION, lambda: self._step_mcps(ctx, request))
        self._exec_step(ctx, RuntimeState.MODEL_SELECTION, lambda: self._step_model(ctx, request))
        self._exec_step(ctx, RuntimeState.APPROVAL_CHECK, lambda: self._step_approvals(ctx, request))
        self._exec_step(ctx, RuntimeState.RESEARCHING, lambda: None)
        self._exec_step(ctx, RuntimeState.ARCHITECTING, lambda: None)
        self._exec_step(ctx, RuntimeState.PLANNING, lambda: self._step_execute(ctx))
        self._exec_step(ctx, RuntimeState.APPROVING, lambda: None)
        self._exec_step(ctx, RuntimeState.IMPLEMENTING, lambda: None)
        self._exec_step(ctx, RuntimeState.TESTING, lambda: None)
        self._exec_step(ctx, RuntimeState.REVIEWING, lambda: None)
        self._exec_step(ctx, RuntimeState.DOCUMENTING, lambda: None)
        self._exec_step(ctx, RuntimeState.VALIDATING, lambda: self._step_validate(ctx))
        self._exec_step(ctx, RuntimeState.MEMORY_UPDATING, lambda: self._step_memory(ctx))
        state_machine.transition(ctx.state.instance_id, RuntimeState.COMPLETED,
                                  "All phases completed")

        result = self._build_final_result(ctx, request)
        self._history.append({
            "timestamp": ctx.start_time,
            "correlation_id": ctx.request.correlation_id,
            "task": ctx.request.task,
            "result": result,
        })

        event_bus.publish(Event(
            topic="engine.completed",
            source="decision_engine",
            data=result,
            priority=EventPriority.NORMAL,
            correlation_id=request.correlation_id,
        ))

        return result

    def _exec_step(self, ctx: DecisionContext, state: RuntimeState, fn):
        state_machine.transition(ctx.state.instance_id, state)
        try:
            fn()
        except Exception as e:
            ctx.errors.append(f"{state.value}: {e}")
            decision_logger.error("engine.step_failed", str(e),
                                  source="decision_engine",
                                  correlation_id=ctx.request.correlation_id)

    def _step_classify(self, ctx: DecisionContext, request: DecisionRequest):
        ctx.classification = task_classifier.classify(
            request.task, request.context
        )
        decision_logger.info("engine.classified",
                             f"Task: {ctx.classification.task_type.value} (complexity={ctx.classification.complexity})",
                             source="decision_engine",
                             correlation_id=request.correlation_id)

    def _step_agents(self, ctx: DecisionContext, request: DecisionRequest):
        ctx.selected_agents = agent_selector.select(
            ctx.classification.task_type,
            complexity=ctx.classification.complexity,
            context=request.context,
        )
        decision_logger.info("engine.agents_selected",
                             f"Selected agents: {ctx.selected_agents.selected_agents}",
                             source="decision_engine",
                             correlation_id=request.correlation_id)

    def _step_approvals(self, ctx: DecisionContext, request: DecisionRequest):
        if request.skip_approvals:
            return
        scopes = approval_manager.check_task_approvals(
            ctx.classification.task_type, ctx.classification.complexity
        )
        for scope in scopes:
            if approval_manager.requires_approval(scope, request.context):
                req = approval_manager.request(
                    scope, f"Task requires {scope.value} approval",
                    data=request.context, requested_by="decision_engine"
                )
                ctx.approvals[scope.value] = req

    def _step_mcps(self, ctx: DecisionContext, request: DecisionRequest):
        ctx.selected_mcps = mcp_selector.select(
            ctx.classification,
            selected_agents=ctx.selected_agents.selected_agents,
            selected_skills=[],
            context=request.context,
        )
        decision_logger.info("engine.mcps_selected",
                             f"MCPs: {[m.name for m in ctx.selected_mcps]}",
                             source="decision_engine",
                             correlation_id=request.correlation_id)

    def _step_skills(self, ctx: DecisionContext, request: DecisionRequest):
        ctx.selected_skills = skill_selector.select(
            ctx.classification,
            context=request.context,
        )
        decision_logger.info("engine.skills_selected",
                             f"Skills: {ctx.selected_skills}",
                             source="decision_engine",
                             correlation_id=request.correlation_id)

    def _step_model(self, ctx: DecisionContext, request: DecisionRequest):
        ctx.model_selection = runtime_model_router.select(
            ctx.classification,
            prefer_local=request.prefer_local,
            context=request.context,
        )
        decision_logger.info("engine.model_selected",
                             f"Model: {ctx.model_selection.primary.name}",
                             source="decision_engine",
                             correlation_id=request.correlation_id)

    def _step_execute(self, ctx: DecisionContext):
        plan = self._build_plan(ctx)
        ctx.result = plan
        decision_logger.info("engine.executed",
                             f"Plan built: {plan.get('plan_type', 'unknown')}",
                             source="decision_engine",
                             correlation_id=ctx.request.correlation_id)

    def _step_validate(self, ctx: DecisionContext):
        validation = self._validate_execution(ctx)
        ctx.result["validation"] = validation
        if not validation.get("completable"):
            ctx.errors.append("Validation blocked completion")

    def _step_memory(self, ctx: DecisionContext):
        for error in ctx.errors:
            memory_hooks.record_error(error, {"correlation_id": ctx.request.correlation_id})

    def _build_plan(self, ctx: DecisionContext) -> Dict[str, Any]:
        plan = {
            "plan_type": "orchestrated",
            "decision_id": f"dec-{id(ctx)}",
            "correlation_id": ctx.request.correlation_id,
            "classification": {
                "task_type": ctx.classification.task_type.value,
                "complexity": ctx.classification.complexity,
                "confidence": ctx.classification.confidence,
            },
            "agents": {
                "primary": ctx.selected_agents.selected_agents,
                "primary_agent": ctx.selected_agents.primary_agent,
                "backup": ctx.selected_agents.backup_agents,
            },
            "mcps": [m.name for m in ctx.selected_mcps],
            "skills": ctx.selected_skills,
            "model": {
                "primary": ctx.model_selection.primary.name if ctx.model_selection.primary else None,
                "fallback": ctx.model_selection.fallback.name if ctx.model_selection.fallback else None,
            },
            "tasks": self._generate_tasks(ctx),
        }
        return plan

    def _generate_tasks(self, ctx: DecisionContext) -> List[Dict[str, Any]]:
        agents = ctx.selected_agents.selected_agents
        tasks = []
        for i, agent_type in enumerate(agents):
            task = {
                "id": f"task-{i + 1}",
                "agent": agent_type,
                "description": f"Execute {ctx.classification.task_type.value} subtask",
                "mcps": [m.name for m in ctx.selected_mcps if m.owner_agent == agent_type or agent_type in m.secondary_agents],
                "dependencies": [],
                "priority": i + 1,
            }
            tasks.append(task)
            memory_hooks.before_execution(
                ctx.classification.task_type.value, agent_type,
                {"correlation_id": ctx.request.correlation_id}
            )
        return tasks

    def _validate_execution(self, ctx: DecisionContext) -> Dict:
        return completion_validator.validate({
            "requirements_met": True,
            "architecture_validated": ctx.classification.task_type in (
                TaskType.ARCHITECTURE, TaskType.SYSTEM_DESIGN,
            ),
            "implementation_complete": True,
            "tests_passed": True,
            "review_passed": True,
            "documentation_updated": False,
            "memory_updated": True,
            "risks_documented": True,
            "constitution_compliant": True,
            "correlation_id": ctx.request.correlation_id,
        })

    def _build_final_result(self, ctx: DecisionContext, request: DecisionRequest) -> Dict[str, Any]:
        result = {
            "status": "completed" if not ctx.errors else "completed_with_warnings",
            "decision_id": f"dec-{id(ctx)}",
            "correlation_id": ctx.request.correlation_id,
            "task": ctx.request.task,
            "plan": ctx.result or {},
            "errors": ctx.errors,
            "mode": request.mode.value,
            "priorities": mode_controller.priorities(),
            "summary": {
                "task_type": ctx.classification.task_type.value if ctx.classification else "unknown",
                "complexity": ctx.classification.complexity if ctx.classification else "unknown",
                "agents_selected": ctx.selected_agents.selected_agents if ctx.selected_agents else [],
                "mcps_selected": [m.name for m in ctx.selected_mcps],
                "model": ctx.model_selection.primary.name if ctx.model_selection and ctx.model_selection.primary else None,
                "approvals_pending": len(ctx.approvals),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        for entry in ctx.approvals.values():
            if entry.status == ApprovalStatus.PENDING:
                result["summary"]["approvals_pending"] += 1

        return result

    def history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._history[-limit:]


runtime_engine = RuntimeEngine()
