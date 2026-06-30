from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

from backend.decision_runtime.registries import agent_registry, AgentCapability
from backend.decision_runtime.task_classifier import TaskType


AGENT_TASK_MAP: Dict[TaskType, List[str]] = {
    TaskType.LEARNING: ["planner", "manager"],
    TaskType.BUG_FIX: ["debugger", "tester", "coder", "reviewer", "manager"],
    TaskType.FEATURE: ["planner", "architect", "coder", "tester", "reviewer", "manager"],
    TaskType.ARCHITECTURE: ["architect", "planner", "manager"],
    TaskType.RESEARCH: ["planner", "manager"],
    TaskType.REFACTOR: ["coder", "tester", "reviewer", "manager"],
    TaskType.DEPLOYMENT: ["manager", "tester", "reviewer"],
    TaskType.RELEASE: ["manager", "tester", "reviewer"],
    TaskType.PERFORMANCE: ["tester", "debugger", "coder", "manager"],
    TaskType.DOCUMENTATION: ["coder", "manager"],
    TaskType.PROJECT_PLANNING: ["planner", "architect", "manager"],
    TaskType.SYSTEM_DESIGN: ["architect", "planner", "manager"],
    TaskType.LARGE_PROJECT: ["architect", "planner", "coder", "tester", "reviewer", "manager"],
    TaskType.REVIEW: ["reviewer", "tester", "manager"],
    TaskType.TESTING: ["tester", "manager"],
    TaskType.DEBUGGING: ["debugger", "coder", "tester", "manager"],
    TaskType.GENERAL: ["manager"],
}


ESCALATION_AGENTS: Dict[str, List[str]] = {
    "architect": ["planner", "manager"],
    "reviewer": ["tester", "manager"],
    "debugger": ["tester", "coder", "manager"],
    "tester": ["coder", "manager"],
    "coder": ["planner", "architect", "manager"],
    "planner": ["architect", "manager"],
}


@dataclass
class SelectionResult:
    selected_agents: List[str]
    primary_agent: str
    backup_agents: List[str]
    escalation_path: List[str]
    all_capabilities: List[str]
    selection_reasoning: str
    requires_manager: bool


class AgentSelector:
    def select(self, task_type: TaskType, complexity: str = "moderate",
                context: Optional[Dict] = None) -> SelectionResult:
        agents = AGENT_TASK_MAP.get(task_type, ["manager"])
        selected: List[str] = []
        capabilities: List[str] = []

        for agent_type in agents:
            cap = agent_registry.get(agent_type)
            if cap and cap.enabled:
                complexity_rank = {"simple": 1, "moderate": 2, "complex": 3, "critical": 4}
                max_rank = complexity_rank.get(cap.max_complexity, 4)
                task_rank = complexity_rank.get(complexity, 2)
                if task_rank <= max_rank:
                    selected.append(agent_type)
                    capabilities.extend(cap.capabilities)

        if not selected:
            selected = ["manager"]
            manager = agent_registry.get("manager")
            if manager:
                capabilities = manager.capabilities

        primary = selected[0] if selected else "manager"
        backup = selected[1:] if len(selected) > 1 else []
        escalation = ESCALATION_AGENTS.get(primary, ["manager"])

        has_manager = "manager" in selected or primary == "manager"
        if not has_manager:
            selected.append("manager")

        return SelectionResult(
            selected_agents=selected,
            primary_agent=primary,
            backup_agents=backup,
            escalation_path=escalation,
            all_capabilities=list(set(capabilities)),
            selection_reasoning=f"Task type '{task_type.value}' → agents: {selected}",
            requires_manager=has_manager,
        )

    def select_by_capability(self, required_capability: str) -> List[str]:
        result = []
        for agent_cap in agent_registry.list():
            if required_capability in agent_cap.capabilities:
                result.append(agent_cap.agent_type)
        return result


agent_selector = AgentSelector()
