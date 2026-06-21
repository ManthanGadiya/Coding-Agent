from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class ComplexityLevel(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


class WorkflowCategory(str, Enum):
    SDLC = "sdlc"
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    REFACTOR = "refactor"
    RELEASE = "release"
    TASK_PIPELINE = "task_pipeline"


@dataclass
class WorkflowStep:
    name: str
    agent: str
    description: str
    action: str = "execute"
    gates: List[str] = field(default_factory=list)
    escalation: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)


@dataclass
class WorkflowBlueprint:
    category: WorkflowCategory
    complexity: ComplexityLevel
    steps: List[WorkflowStep]
    quality_gates: List[str] = field(default_factory=list)
    requires_approval: bool = False
    requires_architect: bool = False
    requires_reviewer: bool = False


def sdlc_workflow(complexity: ComplexityLevel = ComplexityLevel.MODERATE) -> WorkflowBlueprint:
    steps = [
        WorkflowStep("manager_analysis", "manager", "Analyze task, assess risk and complexity"),
        WorkflowStep("workflow_selection", "manager", "Select workflow based on classification"),
    ]
    if complexity in (ComplexityLevel.MODERATE, ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL):
        steps.append(WorkflowStep("research", "planner", "Research requirements and constraints"))
    if complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL):
        steps.append(WorkflowStep("architecture", "architect", "Design architecture solution"))
    if complexity != ComplexityLevel.SIMPLE:
        steps.append(WorkflowStep("planning", "planner", "Create implementation plan"))
    steps.append(WorkflowStep("manager_approval", "manager", "Approve execution authority"))
    steps.append(WorkflowStep("implementation", "coder", "Implement the solution"))
    steps.append(WorkflowStep("testing", "tester", "Run tests and validate"))
    if complexity != ComplexityLevel.SIMPLE:
        steps.append(WorkflowStep("review", "reviewer", "Review implementation quality"))
    steps.append(WorkflowStep("memory_update", "memory", "Update memory with decisions and lessons"))

    return WorkflowBlueprint(
        category=WorkflowCategory.SDLC,
        complexity=complexity,
        steps=steps,
        quality_gates=["Requirements validated", "Tests passed", "Review passed", "Architecture compliance verified"],
        requires_approval=complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL),
        requires_architect=complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL),
        requires_reviewer=complexity != ComplexityLevel.SIMPLE,
    )


def feature_workflow(complexity: ComplexityLevel = ComplexityLevel.MODERATE) -> WorkflowBlueprint:
    steps = [
        WorkflowStep("manager_analysis", "manager", "Analyze feature request and classify"),
        WorkflowStep("feature_classification", "manager", "Classify as simple/moderate/complex/critical"),
    ]
    if complexity != ComplexityLevel.SIMPLE:
        steps.append(WorkflowStep("requirements", "planner", "Define feature requirements"))
    if complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL):
        steps.append(WorkflowStep("research", "planner", "Research technical approach"))
        steps.append(WorkflowStep("architecture", "architect", "Design architecture for feature"))
    if complexity != ComplexityLevel.SIMPLE:
        steps.append(WorkflowStep("planning", "planner", "Create implementation plan"))
    if complexity in (ComplexityLevel.MODERATE, ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL):
        steps.append(WorkflowStep("manager_approval", "manager", "Approve execution plan"))
    steps.append(WorkflowStep("implementation", "coder", "Implement the feature"))
    steps.append(WorkflowStep("testing", "tester", "Test the feature"))
    if complexity != ComplexityLevel.SIMPLE:
        steps.append(WorkflowStep("review", "reviewer", "Review implementation"))
    steps.append(WorkflowStep("memory_update", "memory", "Update memory"))

    return WorkflowBlueprint(
        category=WorkflowCategory.FEATURE,
        complexity=complexity,
        steps=steps,
        quality_gates=["Requirements met", "Tests passed", "Review passed", "Architecture compliant"],
        requires_approval=complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL),
        requires_architect=complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL),
        requires_reviewer=complexity != ComplexityLevel.SIMPLE,
    )


def bug_fix_workflow(complexity: ComplexityLevel = ComplexityLevel.MODERATE, severity: str = "medium") -> WorkflowBlueprint:
    steps = [
        WorkflowStep("manager_analysis", "manager", "Analyze bug report and classify severity"),
        WorkflowStep("bug_classification", "manager", "Classify by type and severity"),
        WorkflowStep("agent_assignment", "manager", "Assign investigation agents"),
        WorkflowStep("investigation", "debugger", "Investigate and find root cause"),
        WorkflowStep("root_cause_analysis", "debugger", "Document root cause with evidence"),
        WorkflowStep("manager_decision", "manager", "Route fix to appropriate agent"),
        WorkflowStep("implementation", "coder", "Implement the fix"),
        WorkflowStep("validation", "tester", "Validate the fix"),
    ]
    if severity in ("high", "critical"):
        steps.insert(8, WorkflowStep("regression_testing", "tester", "Run regression tests"))
    steps.append(WorkflowStep("review", "reviewer", "Review the fix"))
    steps.append(WorkflowStep("knowledge_capture", "memory", "Capture bug knowledge and patterns"))

    return WorkflowBlueprint(
        category=WorkflowCategory.BUG_FIX,
        complexity=ComplexityLevel.MODERATE if severity in ("low", "medium") else ComplexityLevel.COMPLEX,
        steps=steps,
        quality_gates=["Root cause identified", "Fix validated", "Regression tested", "Knowledge captured"],
        requires_approval=severity in ("high", "critical"),
        requires_reviewer=True,
    )


def refactor_workflow(complexity: ComplexityLevel = ComplexityLevel.MODERATE, impact: str = "moderate") -> WorkflowBlueprint:
    steps = [
        WorkflowStep("manager_analysis", "manager", "Analyze refactoring opportunity"),
        WorkflowStep("refactor_classification", "manager", "Classify by impact level"),
    ]
    if impact == "low":
        steps.extend([
            WorkflowStep("implementation", "coder", "Perform refactoring"),
            WorkflowStep("testing", "tester", "Verify no regression"),
        ])
    elif impact == "moderate":
        steps.extend([
            WorkflowStep("planning", "planner", "Create refactoring plan"),
            WorkflowStep("manager_approval", "manager", "Approve plan"),
            WorkflowStep("implementation", "coder", "Execute refactoring"),
            WorkflowStep("testing", "tester", "Run tests"),
        ])
    else:
        steps.extend([
            WorkflowStep("planning", "planner", "Create refactoring plan"),
            WorkflowStep("architecture", "architect", "Design target architecture"),
            WorkflowStep("planning", "planner", "Update plan with architecture"),
            WorkflowStep("manager_approval", "manager", "Approve plan"),
            WorkflowStep("implementation", "coder", "Execute refactoring"),
            WorkflowStep("testing", "tester", "Run tests"),
        ])
    steps.append(WorkflowStep("review", "reviewer", "Review refactoring quality"))
    steps.append(WorkflowStep("memory_update", "memory", "Update technical debt records"))

    return WorkflowBlueprint(
        category=WorkflowCategory.REFACTOR,
        complexity=ComplexityLevel.SIMPLE if impact == "low" else ComplexityLevel.COMPLEX if impact in ("high", "critical") else ComplexityLevel.MODERATE,
        steps=steps,
        quality_gates=["No regression", "Tests pass", "Architecture compliant", "Debt records updated"],
        requires_approval=impact in ("high", "critical"),
        requires_architect=impact in ("high", "critical"),
        requires_reviewer=True,
    )


def release_workflow(complexity: ComplexityLevel = ComplexityLevel.MODERATE, release_type: str = "minor") -> WorkflowBlueprint:
    steps = [
        WorkflowStep("test_validation", "tester", "Run full test suite"),
        WorkflowStep("review_validation", "reviewer", "Assess quality, security, maintainability"),
        WorkflowStep("quality_gate", "manager", "Evaluate quality gate (green/yellow/red)"),
        WorkflowStep("manager_approval", "manager", "Approve release"),
        WorkflowStep("user_awareness", "manager", "Inform user of changes and risks"),
        WorkflowStep("release_execution", "manager", "Execute release"),
        WorkflowStep("monitoring", "tester", "Monitor post-release stability and errors"),
        WorkflowStep("post_release_review", "manager", "Review success and lessons"),
        WorkflowStep("memory_update", "memory", "Store release records and lessons"),
    ]

    return WorkflowBlueprint(
        category=WorkflowCategory.RELEASE,
        complexity=ComplexityLevel.CRITICAL if release_type == "major" else ComplexityLevel.MODERATE,
        steps=steps,
        quality_gates=["Tests passed", "Review passed", "Quality gate passed", "Manager approved"],
        requires_approval=True,
        requires_reviewer=True,
    )


def task_pipeline_workflow(complexity: ComplexityLevel = ComplexityLevel.SIMPLE) -> WorkflowBlueprint:
    if complexity == ComplexityLevel.SIMPLE:
        steps = [
            WorkflowStep("manager_analysis", "manager", "Analyze task"),
            WorkflowStep("implementation", "coder", "Execute task"),
            WorkflowStep("testing", "tester", "Validate result"),
            WorkflowStep("memory_update", "memory", "Update memory"),
        ]
    elif complexity == ComplexityLevel.MODERATE:
        steps = [
            WorkflowStep("manager_analysis", "manager", "Analyze task"),
            WorkflowStep("planning", "planner", "Create plan"),
            WorkflowStep("implementation", "coder", "Execute task"),
            WorkflowStep("testing", "tester", "Validate result"),
            WorkflowStep("review", "reviewer", "Review quality"),
            WorkflowStep("memory_update", "memory", "Update memory"),
        ]
    else:
        steps = [
            WorkflowStep("manager_analysis", "manager", "Analyze task"),
            WorkflowStep("planning", "planner", "Create plan"),
            WorkflowStep("architecture", "architect", "Design solution architecture"),
            WorkflowStep("planning", "planner", "Update plan with architecture"),
            WorkflowStep("implementation", "coder", "Execute task"),
            WorkflowStep("testing", "tester", "Validate result"),
        ]
        if complexity == ComplexityLevel.CRITICAL:
            steps.append(WorkflowStep("review", "reviewer", "Review quality"))
        steps.append(WorkflowStep("memory_update", "memory", "Update memory"))

    return WorkflowBlueprint(
        category=WorkflowCategory.TASK_PIPELINE,
        complexity=complexity,
        steps=steps,
        quality_gates=["Tests passed", "Review passed"] if complexity != ComplexityLevel.SIMPLE else ["Tests passed"],
        requires_approval=complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL),
        requires_architect=complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL),
        requires_reviewer=complexity != ComplexityLevel.SIMPLE,
    )


WORKFLOW_BUILDERS: Dict[str, callable] = {
    "sdlc": sdlc_workflow,
    "feature": feature_workflow,
    "bug_fix": bug_fix_workflow,
    "refactor": refactor_workflow,
    "release": release_workflow,
    "task_pipeline": task_pipeline_workflow,
}


def get_workflow_blueprint(category: str, complexity: str = "moderate", **kwargs) -> Optional[WorkflowBlueprint]:
    builder = WORKFLOW_BUILDERS.get(category)
    if not builder:
        return None
    complexity_enum = ComplexityLevel(complexity) if isinstance(complexity, str) else complexity
    return builder(complexity_enum, **(kwargs if kwargs else {}))


def classify_task(scope: str, risk: str, dependencies: int, architecture_impact: bool,
                  security_impact: bool, research_needed: bool) -> ComplexityLevel:
    score = 0
    if scope == "small": score += 0
    elif scope == "medium": score += 2
    elif scope == "large": score += 5

    if risk == "low": score += 0
    elif risk == "medium": score += 3
    elif risk == "high": score += 6

    if dependencies > 0: score += min(dependencies, 3)
    if architecture_impact: score += 4
    if security_impact: score += 5
    if research_needed: score += 2

    if score <= 2: return ComplexityLevel.SIMPLE
    if score <= 6: return ComplexityLevel.MODERATE
    if score <= 12: return ComplexityLevel.COMPLEX
    return ComplexityLevel.CRITICAL
