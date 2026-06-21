from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import uuid
from datetime import datetime


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

    async def execute_task(self, task: AgentTask) -> AgentResult:
        self.state = AgentState.THINKING
        self.current_task = task
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