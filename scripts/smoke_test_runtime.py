import sys

sys.path.insert(0, ".")  # noqa

from backend.decision_runtime import (
    runtime_engine,
    DecisionRequest,
    EnvironmentMode,
    decision_trace,
    escalation_manager,
    comm_enforcer,
    mode_controller,
    agent_registry,
    skill_registry,
)
from backend.decision_runtime.escalation import SeverityLevel
from backend.decision_runtime.event_bus import event_bus

passed = 0
failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


print("=== CAMera Decision Runtime Smoke Test ===")
print()

# 1. Registry smoke
print("[1] Registry")
check("agents exist", len(agent_registry.list()) >= 6)
check("skills exist", len(skill_registry.list()) >= 8)

# 2. Engine smoke
print("[2] Decision Engine")
r = runtime_engine.decide(
    DecisionRequest(task="add login feature", correlation_id="smoke-001")
)
check("engine returns result", bool(r))
check("status is completed", r.get("status") in ("completed", "completed_with_warnings"))
summary = r.get("summary", {})
check("task type classified", summary.get("task_type") == "feature")
check("agents selected", len(summary.get("agents_selected", [])) > 0)
plan = r.get("plan", {})
skills = plan.get("skills", [])
skill_names = [s.name for s in skills] if skills else []
check("skills selected", len(skill_names) > 0)
check("model selected", bool(summary.get("model")))
check("plan has agents", len(r.get("plan", {}).get("agents", {}).get("primary", [])) > 0)
check("plan has tasks", len(r.get("plan", {}).get("tasks", [])) > 0)

# 3. Decision Trace
print("[3] Decision Trace")
check("trace recorded", decision_trace.summary()["total_decisions"] > 0)
t = decision_trace.find(task="add login feature")
check("trace findable by task", len(t) > 0)
if t:
    check("trace has outcome", bool(t[0].outcome))

# 4. Environment Mode
print("[4] Environment Mode")
mode_controller.set_mode(EnvironmentMode.TEACHING)
check(
    "teaching priorities start with learning",
    mode_controller.priorities()[0] == "learning",
)
mode_controller.set_mode(EnvironmentMode.AUTONOMOUS)
check(
    "autonomous priorities start with correctness",
    mode_controller.priorities()[0] == "correctness",
)
mode_controller.set_mode(EnvironmentMode.BUILD)

# 5. Communication Enforcement
print("[5] Communication")
check(
    "coder->tester allowed",
    comm_enforcer.check("coder", "tester")["allowed"],
)
check(
    "reviewer->architect blocked",
    not comm_enforcer.check("reviewer", "architect")["allowed"],
)
check(
    "memory->all allowed",
    comm_enforcer.check("memory", "architect")["allowed"],
)
check(
    "suggested route exists",
    len(comm_enforcer.check("debugger", "architect").get("suggested_route", [])) > 0,
)

# 6. Escalation
print("[6] Escalation")
e = escalation_manager.escalate(
    "Test escalation", SeverityLevel.WARNING, "testing", "tester"
)
check("escalation created", bool(e.escalation_id))
check("escalation level is 2", e.escalation_level.value == 2)
ep = escalation_manager.emergency_pause("test emergency", "reviewer")
check("emergency pause level is 4", ep.escalation_level.value == 4)
check("emergency targets architect", ep.target_agent == "architect")
sr = escalation_manager.security_escalation("test security", "reviewer")
check("security escalation created", bool(sr.escalation_id))

# 7. Event Bus
print("[7] Event Bus")
events_received = []
event_bus.subscribe("trace.recorded", lambda e: events_received.append(e.topic))
runtime_engine.decide(
    DecisionRequest(task="test event bus", correlation_id="smoke-002")
)
check("trace event published", any("trace" in t for t in events_received))

# 8. Multi-mode requests
print("[8] Multi-mode")
r_teach = runtime_engine.decide(
    DecisionRequest(
        task="explain sorting algorithms", mode=EnvironmentMode.TEACHING
    )
)
check("teaching mode in result", r_teach.get("mode") == "teaching")
r_auto = runtime_engine.decide(
    DecisionRequest(task="deploy to production", mode=EnvironmentMode.AUTONOMOUS)
)
check("autonomous mode in result", r_auto.get("mode") == "autonomous")

print()
print(f"=== Results: {passed} passed, {failed} failed ===")
if failed > 0:
    sys.exit(1)
