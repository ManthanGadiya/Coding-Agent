from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import uuid
from datetime import datetime

from backend.core.model_router import get_model_router
from backend.models.llm import LLMRequest
from backend.tools import get_tool, ToolResult, TOOL_REGISTRY
from backend.core.safety import safety_controller


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
        router = get_model_router()
        resp = await router.generate(LLMRequest(
            prompt=prompt, system_prompt=system_prompt,
            task_type=self.agent_id, max_tokens=max_tokens,
        ))
        return resp.content

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
                response = await self.handle_message(message)
                if response:
                    pass
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
            self.state = AgentState.ERROR
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