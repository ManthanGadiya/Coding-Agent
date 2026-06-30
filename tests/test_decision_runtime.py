import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.decision_runtime import (
    environment_mode, agent_communication,
    escalation, event_bus, mode_controller,
    comm_enforcer, escalation_manager,
)
from backend.decision_runtime import DecisionTrace
from backend.decision_runtime.environment_mode import EnvironmentMode
from backend.decision_runtime.escalation import SeverityLevel, EscalationLevel

passed = 0
failed = 0
errors = []


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS {label}")
    else:
        failed += 1
        msg = f"  FAIL {label}" + (f": {detail}" if detail else "")
        errors.append(msg)
        print(msg)


def test_environment_mode():
    mc = environment_mode.ModeController(EnvironmentMode.BUILD)
    check("build mode default priority is maintainability",
          mc.priorities()[0] == "maintainability")
    check("teaching mode priority is learning",
          mc.priorities(EnvironmentMode.TEACHING)[0] == "learning")
    check("autonomous mode priority is correctness",
          mc.priorities(EnvironmentMode.AUTONOMOUS)[0] == "correctness")

    mc2 = environment_mode.ModeController(EnvironmentMode.TEACHING)
    check("rank returns low for learning in teaching",
          mc2.rank("learning") == 0)
    check("weight returns 1.0 for top priority",
          mc2.weight("learning") == 1.0)
    check("is_higher_priority flags learning > maintainability",
          mc2.is_higher_priority_than("learning", "maintainability"))


def test_decision_trace():
    dt2 = DecisionTrace()
    t1 = dt2.record("fix bug", "Bug identified", evidence=["stack trace"],
                    confidence="high", owner="tester")
    check("trace record has decision_id", bool(t1.decision_id))
    check("trace record has task", t1.task == "fix bug")
    check("trace record has timestamp", bool(t1.timestamp))
    check("trace record has evidence", "stack trace" in t1.evidence)

    dt2.resolve(t1.decision_id, "completed", storage_location="db:123")
    t1_resolved = dt2.get(t1.decision_id)
    check("trace resolved has outcome", t1_resolved.outcome == "completed")
    check("trace resolved has storage", t1_resolved.storage_location == "db:123")

    t2 = dt2.record("add feature", "New feature", owner="coder")
    check("second trace gets new id", t2.decision_id != t1.decision_id)
    check("find by task", len(dt2.find(task="bug")) >= 1)
    check("find by owner", len(dt2.find(owner="coder")) >= 1)

    summary = dt2.summary()
    check("summary has total_decisions",
          summary["total_decisions"] == 2)
    check("summary by_confidence has high",
          summary["by_confidence"].get("high") == 1)

    check("find returns empty for unknown task", len(dt2.find(task="nonexistent")) == 0)
    check("find with no filters returns all", len(dt2.find()) == 2)
    check("find with limit", len(dt2.find(limit=1)) == 1)

    check("get returns None for unknown id",
          dt2.get("nonexistent") is None)
    check("resolve returns None for unknown",
          dt2.resolve("nonexistent", "outcome") is None)

    dt3 = DecisionTrace()
    dt3.record("diff task", "first", owner="alice")
    dt3.record("diff task", "second", owner="bob")
    found = dt3.find(owner="alice")
    check("find filters by owner", all(t.owner == "alice" for t in found))
    found2 = dt3.find(owner="bob")
    check("find filters second owner", all(t.owner == "bob" for t in found2))


def test_communication():
    ce = agent_communication.CommunicationEnforcer()
    check("coder->tester allowed", ce.check("coder", "tester")["allowed"])
    check("manager->architect allowed", ce.check("manager", "architect")["allowed"])
    check("memory->coder allowed", ce.check("memory", "coder")["allowed"])
    check("coder->memory allowed", ce.check("coder", "memory")["allowed"])
    check("reviewer->architect blocked",
          not ce.check("reviewer", "architect")["allowed"])
    check("debugger->architect blocked",
          not ce.check("debugger", "architect")["allowed"])
    check("blocked has suggested_route",
          len(ce.check("reviewer", "architect").get("suggested_route", [])) > 0)

    c1 = ce.check("tester", "reviewer")
    check("tester->reviewer allowed", c1["allowed"])
    check("no violation flag on allowed", "violation" not in c1)

    c2 = ce.check("coder", "planner")
    check("coder->planner allowed", c2["allowed"])

    try:
        ce.enforce("reviewer", "architect")
        check("enforce raises for blocked", False)
    except agent_communication.CommunicationViolation:
        check("enforce raises CommunicationViolation", True)

    allowed_reviewer = ce.allowed("reviewer")
    check("reviewer can talk to manager", "manager" in allowed_reviewer)
    check("reviewer can talk to tester", "tester" in allowed_reviewer)
    check("reviewer NOT allowed architect", "architect" not in allowed_reviewer)

    check("can_communicate helper", ce.can_communicate("coder", "tester"))
    check("can_communicate helper blocked", not ce.can_communicate("reviewer", "architect"))

    violations = ce.violations()
    check("violations tracked", len(violations) > 0)
    check("all violations have violation flag",
          all(v.get("violation") for v in violations))

    try:
        ce.check("unknown_agent", "coder")
        check("rejects unknown sender", False)
    except ValueError:
        check("rejects unknown sender", True)

    try:
        ce.check("coder", "unknown_agent")
        check("rejects unknown receiver", False)
    except ValueError:
        check("rejects unknown receiver", True)


def test_escalation():
    em = escalation.EscalationManager()
    e1 = em.escalate("Test issue", SeverityLevel.WARNING, "testing", "tester")
    check("escalation has id", bool(e1.escalation_id))
    check("escalation level is AGENT_TO_MANAGER",
          e1.escalation_level == EscalationLevel.AGENT_TO_MANAGER)
    check("escalation severity is WARNING",
          e1.severity == SeverityLevel.WARNING)
    check("escalation targets manager", e1.target_agent == "manager")
    check("escalation status open", e1.status == "open")

    em.resolve(e1.escalation_id, "Issue fixed", "resolved")
    resolved = em.get(e1.escalation_id)
    check("resolved status", resolved.status == "resolved")
    check("resolved outcome", resolved.outcome == "resolved")
    check("resolved resolution text", resolved.resolution == "Issue fixed")

    ep = em.emergency_pause("Critical security hole", "reviewer")
    check("emergency pause level is EMERGENCY",
          ep.escalation_level == EscalationLevel.EMERGENCY)
    check("emergency pause targets architect", ep.target_agent == "architect")
    check("emergency pause severity is EMERGENCY",
          ep.severity == SeverityLevel.EMERGENCY)

    er = em.emergency_rollback("Data corruption risk", "coder")
    check("emergency rollback level is EMERGENCY",
          er.escalation_level == EscalationLevel.EMERGENCY)
    check("emergency rollback targets architect", er.target_agent == "architect")

    es = em.security_escalation("Credential leak", "reviewer")
    check("security escalation level is MANAGER_TO_USER",
          es.escalation_level == EscalationLevel.MANAGER_TO_USER)
    check("security escalation severity is CRITICAL",
          es.severity == SeverityLevel.CRITICAL)
    check("security escalation targets manager", es.target_agent == "manager")

    summary = em.summary()
    check("summary total matches", summary["total"] == 4)
    check("summary has by_severity", "EMERGENCY" in summary["by_severity"])
    check("summary has by_status", "open" in summary["by_status"])

    found = em.find(source_agent="reviewer")
    check("find by source_agent", len(found) >= 2)
    check("all found match agent",
          all(f.source_agent == "reviewer" for f in found))

    found2 = em.find(severity=SeverityLevel.EMERGENCY)
    check("find by severity", len(found2) >= 2)

    found3 = em.find(status="resolved")
    check("find by status resolved", len(found3) >= 1)

    check("get returns None for unknown id",
          em.get("nonexistent") is None)

    e2 = em.escalate(
        "Info", SeverityLevel.INFORMATIONAL, "low impact", "planner",
        evidence=["doc1", "doc2"],
        recommendations=["suggestion"],
        confidence="high",
    )
    check("escalation with full metadata", bool(e2.escalation_id))
    check("evidence stored", "doc1" in e2.evidence)
    check("recommendations stored", "suggestion" in e2.recommendations)
    check("INFORMATIONAL maps to AGENT_TO_AGENT",
          e2.escalation_level == EscalationLevel.AGENT_TO_AGENT)


def test_event_bus():
    eb = event_bus.EventBus()
    received = []

    def handler(event):
        received.append(event)

    eb.subscribe("test.event", handler)
    eb.publish(event_bus.Event(topic="test.event", source="test",
                               data={"msg": "hello"}))

    check("handler called", len(received) == 1)
    check("correct event data", received[0].data["msg"] == "hello")

    eb.unsubscribe("test.event", handler)
    eb.publish(event_bus.Event(topic="test.event", source="test", data={}))
    check("unsubscribed handler not called", len(received) == 1)

    received2 = []
    def h2(e):
        received2.append(e.topic)

    eb.subscribe("evt.a", h2)
    eb.subscribe("evt.b", h2)
    eb.publish(event_bus.Event(topic="evt.a", source="test", data={}))
    eb.publish(event_bus.Event(topic="evt.b", source="test", data={}))
    check("multiple subscriptions work", len(received2) == 2)

    hist = eb.get_history()
    check("event bus has history", isinstance(hist, list))
    check("history contains events", len(hist) > 0)


def test_misc():
    check("mode_controller singleton exits", bool(mode_controller))
    from backend.decision_runtime import decision_trace as dt_singleton
    check("decision_trace singleton exits", isinstance(dt_singleton, DecisionTrace))
    check("comm_enforcer singleton exits", bool(comm_enforcer))
    check("escalation_manager singleton exits", bool(escalation_manager))


if __name__ == "__main__":
    print("=" * 60)
    print("CAMera Decision Runtime Unit Tests")
    print("=" * 60)
    print()

    print("[environment_mode]")
    test_environment_mode()
    print()

    print("[decision_trace]")
    test_decision_trace()
    print()

    print("[agent_communication]")
    test_communication()
    print()

    print("[escalation]")
    test_escalation()
    print()

    print("[event_bus]")
    test_event_bus()
    print()

    print("[misc]")
    test_misc()
    print()

    print("=" * 60)
    total = passed + failed
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if errors:
        print("Failures:")
        for e in errors:
            print(e)
    print("=" * 60)
    sys.exit(1 if failed > 0 else 0)
