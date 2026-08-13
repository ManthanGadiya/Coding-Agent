from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import uuid
from datetime import datetime

from backend.core.model_router import get_model_router
from backend.models.llm import LLMRequest
from backend.tools import get_tool, ToolResult
from backend.core.safety import safety_controller

# Hints for the decision_runtime per-task-type router (values are TaskType names).
# Used by _llm_generate() when the runtime router is available; otherwise the core
# router's existing behavior is preserved.
_AGENT_TASK_TYPES = {
    "implement": "feature", "create_file": "feature", "modify_file": "feature",
    "refactor": "refactor", "fix": "bug_fix", "run_test": "testing",
    "run_lint": "testing", "run_build": "deployment",
    "architecture_design": "architecture", "system_design": "system_design",
    "research": "research", "plan_generation": "project_planning",
    "write_test": "testing", "check_coverage": "testing", "run_test_suite": "testing",
    "diagnose": "debugging", "analyze_error": "debugging", "trace": "debugging",
    "suggest_fix": "debugging", "reproduce": "debugging",
    "review_code": "review", "review_architecture": "review", "review_security": "review",
}
_AGENT_ROLE_TYPES = {
    "architect": "architecture", "coder": "feature", "tester": "testing",
    "debugger": "debugging", "reviewer": "review", "planner": "project_planning",
    "manager": "general", "memory": "documentation",
}
# Runtime router ModelDef.tier -> core router complexity (TASK_MODEL_MAP keys)
_TIER_COMPLEXITY = {
    "small": "simple", "medium": "moderate", "large": "complex",
    "fast": "critical", "balanced": "critical", "reasoning": "critical",
}


class AgentState(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentMessage:
    sender: str
    receiver: str
    content: str
    objective: str = ""
    evidence: str = ""
    recommendation: str = ""
    next_action: str = ""
    message_type: str = "info"
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AgentTask:
    task_id: str
    task_type: str
    description: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    deadline: Optional[datetime] = None


@dataclass
class AgentResult:
    task_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    completed_at: datetime = field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        name: str,
        capabilities: List[str],
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.config = config or {}
        self.state = AgentState.IDLE
        self.current_task: Optional[AgentTask] = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task_history: List[AgentResult] = []

    async def _llm_generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 1024) -> str:
        req = LLMRequest(
            prompt=prompt, system_prompt=system_prompt,
            task_type=self.agent_id, max_tokens=max_tokens,
            context={"agent_id": self.agent_id},
        )
        try:
            # Route through the decision_runtime per-task-type router when available.
            from backend.decision_runtime.task_classifier import task_classifier, TaskType, ClassificationResult
            from backend.decision_runtime.model_router import runtime_model_router
            selection = runtime_model_router.select(
                self._runtime_classification(prompt, task_classifier, TaskType, ClassificationResult),
                prefer_local=False,  # honor MODEL_TASK_MAP (Architecture->cloud-reasoning, Testing->local-small)
                context=req.context,
            )
            if selection.primary:
                req.context["complexity"] = _TIER_COMPLEXITY.get(selection.primary.tier, "moderate")
                req.context["model_route"] = selection.primary.name
                req.context["model_reasoning"] = selection.reasoning
                req.context["model_cost"] = selection.estimated_cost
                req.context["model_latency_ms"] = selection.estimated_latency_ms
        except Exception:
            pass  # runtime router unavailable -> core router default behavior (backward compatible)
        try:
            resp = await get_model_router().generate(req)
            if not resp.content:
                return "LLM generate returned an empty response"
            return resp.content
        except Exception as e:
            return f"LLM generate failed: {e}"

    def _runtime_classification(self, prompt: str, task_classifier, TaskType, ClassificationResult) -> ClassificationResult:
        """Pick a TaskType for the runtime router: current task type -> agent role -> prompt classification."""
        task_type = None
        if self.current_task and self.current_task.task_type:
            task_type = _AGENT_TASK_TYPES.get(self.current_task.task_type)
        if task_type is None:
            task_type = _AGENT_ROLE_TYPES.get(self.agent_id.split("-")[0])
        if task_type is not None:
            return ClassificationResult(
                task_type=TaskType(task_type), confidence=0.9,
                complexity="moderate", complexity_score=4, scope="medium", risk="low",
            )
        return task_classifier.classify(prompt)

    @abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResult:
        pass

    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        pass

    async def start(self):
        self._running = True
        asyncio.create_task(self._message_loop())

    async def stop(self):
        self._running = False

    async def _message_loop(self):
        while self._running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self.handle_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.state = AgentState.ERROR

    async def send_message(self, receiver: str, content: str, message_type: str = "info", metadata: Optional[Dict] = None) -> AgentMessage:
        message = AgentMessage(
            sender=self.agent_id,
            receiver=receiver,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        return message

    async def _safety_check(self, task: AgentTask) -> Optional[AgentResult]:
        task_desc = task.description or ""
        check = safety_controller.check_pre_operation(self.agent_id, task_desc, str(task.input_data))
        if not check["safe_to_proceed"]:
            return AgentResult(task_id=task.task_id, success=False, error=f"Safety block: {check['impact']['recommendation']}", metadata={"safety_check": check})
        return None

    async def _run_tool(self, tool_name: str, **kwargs) -> ToolResult:
        tool = get_tool(tool_name)
        if not tool:
            return ToolResult(success=False, error=f"Unknown tool: {tool_name}")
        return await tool.safe_execute(agent_id=self.agent_id, **kwargs)

    async def execute_task(self, task: AgentTask) -> AgentResult:
        self.state = AgentState.THINKING
        self.current_task = task
        blocked = await self._safety_check(task)
        if blocked:
            self._task_history.append(blocked)
            self.state = AgentState.IDLE
            self.current_task = None
            return blocked
        try:
            result = await self.process_task(task)
            self._task_history.append(result)
            self.state = AgentState.COMPLETED if result.success else AgentState.ERROR
            return result
        except Exception as e:
            result = AgentResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                confidence=0.0
            )
            self._task_history.append(result)
            self.state = AgentState.ERROR
            return result
        finally:
            self.state = AgentState.IDLE
            self.current_task = None

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state.value,
            "capabilities": self.capabilities,
            "current_task": self.current_task.task_id if self.current_task else None,
            "tasks_completed": len([r for r in self._task_history if r.success]),
            "tasks_failed": len([r for r in self._task_history if not r.success]),
        }

    def can_handle(self, task_type: str) -> bool:
        return task_type in self.capabilities