import pytest
from backend.decision_runtime.conflict_resolver import conflict_resolver, ConflictSeverity
from backend.core.workflow_engine import evaluate_quality_gate, evaluate_completion_criteria


def test_conflict_resolver_consensus():
    result = conflict_resolver.resolve(
        agents=["planner", "architect"],
        issue="Architecture approach",
        arguments={"planner": "Microservices would enable independent scaling",
                    "architect": "Modular monolith is simpler and cheaper"},
        evidence={"planner": ["scaling_requirements.pdf"], "architect": ["cost_analysis.csv"]},
        severity="medium",
    )
    assert result["outcome"] in ("resolved", "escalated_to_user")
    assert result["issue"] == "Architecture approach"
    assert "planner" in result["agents"]
    assert "architect" in result["agents"]


def test_conflict_resolver_arbitration():
    result = conflict_resolver.resolve(
        agents=["coder", "architect", "reviewer"],
        issue="Implementation approach",
        arguments={"coder": "Working implementation in 2 days",
                    "architect": "Does not follow the architecture pattern",
                    "reviewer": "Security concerns with the proposed approach"},
        severity="critical",
    )
    assert result["severity"] == "critical"
    assert len(result["agents"]) == 3


def test_conflict_resolver_single_agent_no_conflict():
    result = conflict_resolver.resolve(
        agents=["planner"],
        issue="Simple decision",
        arguments={"planner": "Just do it"},
        severity="low",
    )
    assert result["outcome"] == "resolved"


def test_quality_gate_all_passed():
    result = evaluate_quality_gate([
        {"name": "Tests", "passed": True, "weight": 3.0},
        {"name": "Review", "passed": True, "weight": 2.0},
    ])
    assert result["passed"] is True
    assert result["score"] == 100.0


def test_quality_gate_failures():
    result = evaluate_quality_gate([
        {"name": "Tests", "passed": False, "weight": 3.0},
        {"name": "Review", "passed": True, "weight": 2.0},
    ])
    assert result["passed"] is False
    assert "Tests" in result["failed_gates"]
    assert result["score"] == 40.0


def test_completion_criteria_blocking():
    result = evaluate_completion_criteria({
        "requirements_met": False,
        "architecture_verified": False,
        "implementation_complete": False,
        "tests_passed": False,
        "review_passed": False,
    })
    assert "Critical requirements missing" in result["blocking_conditions"]


def test_completion_criteria_passes():
    result = evaluate_completion_criteria({
        "requirements_met": True,
        "architecture_verified": True,
        "implementation_complete": True,
        "tests_passed": True,
        "review_passed": True,
        "documentation_updated": True,
        "memory_updated": True,
        "risks_documented": True,
    })
    assert result.get("overall") == "green"
