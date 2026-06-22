from typing import Dict, Optional, Type

from backend.agents.base import BaseAgent
from backend.agents.coder import CoderAgent
from backend.agents.reviewer import ReviewerAgent
from backend.agents.tester import TesterAgent
from backend.agents.memory import MemoryAgent
from backend.agents.debugger import DebuggerAgent
from backend.agents.manager import ManagerAgent
from backend.agents.architect import ArchitectAgent
from backend.agents.planner import PlannerAgent

AGENT_REGISTRY: Dict[str, type] = {
    "coder": CoderAgent,
    "reviewer": ReviewerAgent,
    "tester": TesterAgent,
    "memory": MemoryAgent,
    "debugger": DebuggerAgent,
    "manager": ManagerAgent,
    "architect": ArchitectAgent,
    "planner": PlannerAgent,
}


def create_agent(agent_type: str, agent_id: Optional[str] = None, config: Optional[dict] = None) -> Optional[BaseAgent]:
    agent_cls = AGENT_REGISTRY.get(agent_type)
    if not agent_cls:
        return None
    if not agent_id:
        agent_id = f"{agent_type}-1"
    return agent_cls(agent_id=agent_id, config=config)


_manager_instance = None

def get_manager() -> ManagerAgent:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ManagerAgent()
    return _manager_instance


__all__ = [
    "BaseAgent", "CoderAgent", "ReviewerAgent", "TesterAgent",
    "MemoryAgent", "DebuggerAgent", "ManagerAgent", "ArchitectAgent", "PlannerAgent",
    "AGENT_REGISTRY", "create_agent", "get_manager",
]
