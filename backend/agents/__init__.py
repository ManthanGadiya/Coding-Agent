from typing import Dict, Optional, Type

from backend.agents.base import BaseAgent
from backend.agents.coder import CoderAgent
from backend.agents.reviewer import ReviewerAgent
from backend.agents.tester import TesterAgent
from backend.agents.memory import MemoryAgent
from backend.agents.debugger import DebuggerAgent
from backend.agents.orchestrator import OrchestratorAgent

AGENT_REGISTRY: Dict[str, type] = {
    "coder": CoderAgent,
    "reviewer": ReviewerAgent,
    "tester": TesterAgent,
    "memory": MemoryAgent,
    "debugger": DebuggerAgent,
    "orchestrator": OrchestratorAgent,
}


def create_agent(agent_type: str, agent_id: Optional[str] = None, config: Optional[dict] = None) -> Optional[BaseAgent]:
    agent_cls = AGENT_REGISTRY.get(agent_type)
    if not agent_cls:
        return None
    if not agent_id:
        agent_id = f"{agent_type}-1"
    return agent_cls(agent_id=agent_id, config=config)


def get_orchestrator() -> OrchestratorAgent:
    return OrchestratorAgent()


__all__ = [
    "BaseAgent", "CoderAgent", "ReviewerAgent", "TesterAgent",
    "MemoryAgent", "DebuggerAgent", "OrchestratorAgent",
    "AGENT_REGISTRY", "create_agent", "get_orchestrator",
]