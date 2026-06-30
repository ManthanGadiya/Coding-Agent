from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentCapability:
    agent_type: str
    display_name: str
    capabilities: List[str]
    permissions: List[str]
    allowed_tools: List[str]
    models: List[str]
    max_complexity: str = "complex"
    cost_per_task: float = 1.0
    enabled: bool = True


@dataclass
class SkillDef:
    name: str
    description: str
    activate_conditions: List[str]
    task_types: List[str]
    required_agents: List[str]
    required_mcps: List[str]
    enabled: bool = True


@dataclass
class MCPDef:
    name: str
    description: str
    owner_agent: str
    secondary_agents: List[str] = field(default_factory=list)
    protocols: List[str] = field(default_factory=lambda: ["http"])
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelDef:
    name: str
    provider: str
    tier: str
    context_size: int
    cost_per_token: float
    capabilities: List[str] = field(default_factory=list)
    enabled: bool = True
    latency_ms: int = 1000


@dataclass
class WorkflowStep:
    name: str
    type: str
    config: Dict[str, Any] = field(default_factory=dict)
    handler: Optional[str] = None
    timeout_seconds: int = 300


@dataclass
class WorkflowDef:
    name: str
    description: str
    task_types: List[str]
    steps: List[WorkflowStep]
    quality_gates: List[str] = field(default_factory=list)
    requires_approval: bool = False
    enabled: bool = True


class BaseRegistry:
    def __init__(self):
        self._items: Dict[str, Any] = {}

    def register(self, key: str, item: Any):
        self._items[key] = item

    def get(self, key: str) -> Optional[Any]:
        return self._items.get(key)

    def list(self, enabled_only: bool = True) -> List[Any]:
        items = self._items.values()
        if enabled_only:
            items = [i for i in items if getattr(i, "enabled", True)]
        return list(items)

    def find(self, **filters) -> List[Any]:
        results = self.list()
        for attr, value in filters.items():
            results = [i for i in results if getattr(i, attr, None) == value]
        return results

    def remove(self, key: str):
        self._items.pop(key, None)

    def clear(self):
        self._items.clear()


class AgentRegistry(BaseRegistry):
    pass


class SkillRegistry(BaseRegistry):
    def find_by_task_type(self, task_type: str) -> List[SkillDef]:
        return [s for s in self.list() if task_type in s.task_types]

    def find_by_condition(self, condition: str) -> List[SkillDef]:
        return [s for s in self.list() if condition in s.activate_conditions]


class MCPRegistry(BaseRegistry):
    pass


class ModelRegistry(BaseRegistry):
    pass


class WorkflowRegistry(BaseRegistry):
    def find_by_task_type(self, task_type: str) -> List[WorkflowDef]:
        return [w for w in self.list() if task_type in w.task_types]


agent_registry = AgentRegistry()
skill_registry = SkillRegistry()
mcp_registry = MCPRegistry()
model_registry = ModelRegistry()
workflow_registry = WorkflowRegistry()


def _init_default_registries():
    agent_registry.register("manager", AgentCapability(
        agent_type="manager", display_name="Manager Agent",
        capabilities=["route_task", "assign_agent", "monitor_progress", "resolve_conflict",
                       "manage_workflow", "report_status", "classify_task", "assess_complexity"],
        permissions=["all"], allowed_tools=["all"], models=["all"],
    ))
    agent_registry.register("architect", AgentCapability(
        agent_type="architect", display_name="Architect Agent",
        capabilities=["architecture_design", "technology_selection", "tradeoff_analysis",
                       "risk_assessment", "scalability_evaluation", "architecture_review", "system_design"],
        permissions=["read", "research"], allowed_tools=["firecrawl", "markitdown", "memory"],
        models=["large", "cloud"], max_complexity="critical",
    ))
    agent_registry.register("planner", AgentCapability(
        agent_type="planner", display_name="Planner Agent",
        capabilities=["research", "requirement_analysis", "task_decomposition",
                       "plan_generation", "risk_analysis", "effort_estimation",
                       "roadmap_creation", "technology_comparison", "knowledge_evaluation"],
        permissions=["read", "research"], allowed_tools=["firecrawl", "markitdown", "browser", "websearch"],
        models=["medium", "large"], max_complexity="critical",
    ))
    agent_registry.register("coder", AgentCapability(
        agent_type="coder", display_name="Coder Agent",
        capabilities=["implement", "refactor", "fix", "create_file", "modify_file",
                       "run_build", "run_test", "run_lint"],
        permissions=["read", "write", "execute"], allowed_tools=["filesystem", "terminal", "git", "docker"],
        models=["small", "medium", "large"],
    ))
    agent_registry.register("tester", AgentCapability(
        agent_type="tester", display_name="Tester Agent",
        capabilities=["write_test", "run_test", "run_test_suite", "check_coverage", "validate_behavior"],
        permissions=["read", "execute"], allowed_tools=["terminal", "test_framework", "benchmark", "health"],
        models=["small", "medium"],
    ))
    agent_registry.register("debugger", AgentCapability(
        agent_type="debugger", display_name="Debugger Agent",
        capabilities=["diagnose", "analyze_error", "trace", "check_logs", "reproduce", "suggest_fix"],
        permissions=["read", "execute"], allowed_tools=["terminal", "logs", "investigate", "benchmark", "health"],
        models=["medium", "large"],
    ))
    agent_registry.register("reviewer", AgentCapability(
        agent_type="reviewer", display_name="Reviewer Agent",
        capabilities=["review_code", "review_architecture", "review_security",
                       "review_maintainability", "review_complexity", "approve", "reject"],
        permissions=["read"], allowed_tools=["review", "health", "benchmark"],
        models=["medium", "large"],
    ))
    agent_registry.register("memory", AgentCapability(
        agent_type="memory", display_name="Memory Agent",
        capabilities=["store", "retrieve", "search", "prune", "get_context", "list_by_project"],
        permissions=["read", "write"], allowed_tools=["agent_memory_mcp"],
        models=["small"],
    ))

    skill_registry.register("autoplan", SkillDef(
        name="autoplan", description="Multi-stage project auto-planning",
        activate_conditions=["large_project", "multi_stage", "complex_engineering"],
        task_types=["large_project", "system_design", "architecture"],
        required_agents=["planner", "architect", "manager"],
        required_mcps=["agent_memory"],
    ))
    skill_registry.register("investigate", SkillDef(
        name="investigate", description="Root cause investigation for unknown bugs",
        activate_conditions=["unknown_root_cause", "major_bug", "regression"],
        task_types=["bug_fix", "debugging", "performance"],
        required_agents=["debugger", "tester", "coder"],
        required_mcps=[],
    ))
    skill_registry.register("review", SkillDef(
        name="review", description="Code and architecture review before merge",
        activate_conditions=["major_merge", "pre_merge", "quality_check"],
        task_types=["review", "refactor", "feature"],
        required_agents=["reviewer", "tester"],
        required_mcps=["github"],
    ))
    skill_registry.register("benchmark", SkillDef(
        name="benchmark", description="Performance benchmarking",
        activate_conditions=["performance_critical", "regression_check"],
        task_types=["performance", "optimization"],
        required_agents=["tester"],
        required_mcps=[],
    ))
    skill_registry.register("health", SkillDef(
        name="health", description="Codebase health check before release",
        activate_conditions=["pre_release", "major_change"],
        task_types=["release", "deployment"],
        required_agents=["tester", "reviewer"],
        required_mcps=[],
    ))
    skill_registry.register("design-review", SkillDef(
        name="design-review", description="UI/UX design review",
        activate_conditions=["ui_change", "ux_change", "visual_update"],
        task_types=["feature", "design"],
        required_agents=["reviewer"],
        required_mcps=[],
    ))
    skill_registry.register("plan-eng-review", SkillDef(
        name="plan-eng-review", description="Engineering plan review",
        activate_conditions=["architecture_sensitive", "complex_plan"],
        task_types=["architecture", "planning", "system_design"],
        required_agents=["architect", "planner"],
        required_mcps=[],
    ))
    skill_registry.register("plan-ceo-review", SkillDef(
        name="plan-ceo-review", description="Scope and strategy review",
        activate_conditions=["scope_decision", "strategic", "expansion"],
        task_types=["planning", "project_planning"],
        required_agents=["manager"],
        required_mcps=[],
    ))
    skill_registry.register("plan-devex-review", SkillDef(
        name="plan-devex-review", description="Developer experience evaluation",
        activate_conditions=["devex_evaluation", "api_design", "sdk_work"],
        task_types=["design", "architecture"],
        required_agents=["planner", "reviewer"],
        required_mcps=[],
    ))
    skill_registry.register("agent-browser", SkillDef(
        name="agent-browser", description="Website automation and testing",
        activate_conditions=["website_interaction", "browser_testing", "data_extraction"],
        task_types=["testing", "research", "qa"],
        required_agents=["tester"],
        required_mcps=["agent_browser_mcp"],
    ))
    skill_registry.register("temp_websearch_skill", SkillDef(
        name="temp_websearch_skill", description="General web research",
        activate_conditions=["research_needed", "info_gathering", "documentation_lookup"],
        task_types=["research", "planning", "architecture"],
        required_agents=["planner"],
        required_mcps=[],
    ))

    mcp_registry.register("agent_memory", MCPDef(
        name="agent_memory", description="Agent Memory MCP for knowledge persistence",
        owner_agent="memory", secondary_agents=["manager", "planner"],
    ))
    mcp_registry.register("firecrawl", MCPDef(
        name="firecrawl", description="Firecrawl MCP for web research and documentation",
        owner_agent="planner", secondary_agents=["architect", "manager"],
    ))
    mcp_registry.register("github", MCPDef(
        name="github", description="GitHub MCP for repository management",
        owner_agent="manager", secondary_agents=["coder"],
    ))
    mcp_registry.register("markitdown", MCPDef(
        name="markitdown", description="MarkItDown MCP for document conversion",
        owner_agent="planner", secondary_agents=["architect"],
    ))
    mcp_registry.register("composio", MCPDef(
        name="composio", description="Composio MCP for external integrations",
        owner_agent="manager",
    ))
    mcp_registry.register("hermes", MCPDef(
        name="hermes", description="Hermes Agent MCP for advanced orchestration",
        owner_agent="manager",
    ))
    mcp_registry.register("ruflo", MCPDef(
        name="ruflo", description="Ruflo MCP for workflow support",
        owner_agent="manager",
    ))

    model_registry.register("local-small", ModelDef(
        name="local-small", provider="ollama", tier="small",
        context_size=4096, cost_per_token=0.0,
        capabilities=["simple_tasks", "classification", "formatting"],
        latency_ms=200,
    ))
    model_registry.register("local-medium", ModelDef(
        name="local-medium", provider="ollama", tier="medium",
        context_size=8192, cost_per_token=0.0,
        capabilities=["code_generation", "testing", "debugging"],
        latency_ms=500,
    ))
    model_registry.register("local-large", ModelDef(
        name="local-large", provider="ollama", tier="large",
        context_size=32768, cost_per_token=0.0,
        capabilities=["reasoning", "architecture", "planning", "code_review"],
        latency_ms=2000,
    ))
    model_registry.register("cloud-fast", ModelDef(
        name="cloud-fast", provider="anthropic", tier="fast",
        context_size=128000, cost_per_token=3.0,
        capabilities=["simple_tasks", "classification", "quick_generation"],
        latency_ms=800,
    ))
    model_registry.register("cloud-balanced", ModelDef(
        name="cloud-balanced", provider="anthropic", tier="balanced",
        context_size=128000, cost_per_token=15.0,
        capabilities=["reasoning", "code_generation", "testing", "debugging", "review"],
        latency_ms=2000,
    ))
    model_registry.register("cloud-reasoning", ModelDef(
        name="cloud-reasoning", provider="anthropic", tier="reasoning",
        context_size=200000, cost_per_token=75.0,
        capabilities=["complex_reasoning", "architecture", "strategic", "security_review"],
        latency_ms=5000,
    ))

    workflow_registry.register("sdlc", WorkflowDef(
        name="sdlc", description="Full SDLC workflow",
        task_types=["feature", "architecture", "system_design", "large_project"],
        steps=[
            {"name": "manager_analysis", "agent": "manager", "action": "classify"},
            {"name": "research", "agent": "planner", "action": "research"},
            {"name": "architecture", "agent": "architect", "action": "design"},
            {"name": "planning", "agent": "planner", "action": "plan"},
            {"name": "implementation", "agent": "coder", "action": "implement"},
            {"name": "testing", "agent": "tester", "action": "test"},
            {"name": "review", "agent": "reviewer", "action": "review"},
            {"name": "memory_update", "agent": "memory", "action": "store"},
        ],
        quality_gates=["Requirements validated", "Tests passed", "Review passed"],
        requires_approval=True,
    ))
    workflow_registry.register("bug_fix", WorkflowDef(
        name="bug_fix", description="Bug fixing workflow",
        task_types=["bug_fix", "debugging", "error"],
        steps=[
            {"name": "classification", "agent": "manager", "action": "classify"},
            {"name": "investigation", "agent": "debugger", "action": "investigate"},
            {"name": "fix", "agent": "coder", "action": "implement"},
            {"name": "validation", "agent": "tester", "action": "test"},
            {"name": "review", "agent": "reviewer", "action": "review"},
            {"name": "memory_update", "agent": "memory", "action": "store"},
        ],
        quality_gates=["Root cause identified", "Fix validated"],
    ))
    workflow_registry.register("feature", WorkflowDef(
        name="feature", description="Feature development workflow",
        task_types=["feature", "enhancement"],
        steps=[
            {"name": "analysis", "agent": "manager", "action": "classify"},
            {"name": "planning", "agent": "planner", "action": "plan"},
            {"name": "implementation", "agent": "coder", "action": "implement"},
            {"name": "testing", "agent": "tester", "action": "test"},
            {"name": "review", "agent": "reviewer", "action": "review"},
            {"name": "memory_update", "agent": "memory", "action": "store"},
        ],
        quality_gates=["Tests passed", "Review passed"],
    ))
    workflow_registry.register("refactor", WorkflowDef(
        name="refactor", description="Code refactoring workflow",
        task_types=["refactor", "cleanup", "optimization"],
        steps=[
            {"name": "analysis", "agent": "manager", "action": "classify"},
            {"name": "planning", "agent": "planner", "action": "plan"},
            {"name": "implementation", "agent": "coder", "action": "implement"},
            {"name": "testing", "agent": "tester", "action": "test"},
            {"name": "review", "agent": "reviewer", "action": "review"},
            {"name": "memory_update", "agent": "memory", "action": "store"},
        ],
        quality_gates=["No regression", "Tests pass"],
    ))
    workflow_registry.register("release", WorkflowDef(
        name="release", description="Release workflow",
        task_types=["release", "deployment"],
        steps=[
            {"name": "validation", "agent": "tester", "action": "test"},
            {"name": "quality_gate", "agent": "manager", "action": "evaluate"},
            {"name": "approval", "agent": "manager", "action": "approve"},
            {"name": "execute", "agent": "manager", "action": "execute"},
            {"name": "monitor", "agent": "tester", "action": "monitor"},
            {"name": "memory_update", "agent": "memory", "action": "store"},
        ],
        quality_gates=["Tests passed", "Quality gate passed", "Manager approved"],
        requires_approval=True,
    ))
    workflow_registry.register("research", WorkflowDef(
        name="research", description="Research workflow",
        task_types=["research", "investigation", "learning"],
        steps=[
            {"name": "definition", "agent": "planner", "action": "define"},
            {"name": "gather", "agent": "planner", "action": "research"},
            {"name": "analyze", "agent": "planner", "action": "analyze"},
            {"name": "report", "agent": "planner", "action": "report"},
            {"name": "memory_update", "agent": "memory", "action": "store"},
        ],
    ))


_init_default_registries()
