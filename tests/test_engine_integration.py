import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.decision_runtime.decision_engine import runtime_engine, DecisionRequest
from backend.decision_runtime.environment_mode import EnvironmentMode
from backend.decision_runtime.state_machine import state_machine, RuntimeState
from backend.decision_runtime.completion_validator import completion_validator

passed = 0
failed = 0
errors = []

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        msg = f"  FAIL {label}" + (f": {detail}" if detail else "")
        errors.append(msg)

def test_runtime_engine_decide_pipeline():
    runtime_engine._dispatched.clear()
    req = DecisionRequest(
        task="fix edge case in user login validation",
        context={"complexity": "simple", "language": "python"},
        source="test",
        mode=EnvironmentMode.BUILD,
        skip_approvals=True,
    )
    result = runtime_engine.decide(req)

    check("engine returns completed status",
          result["status"] == "completed" or result["status"] == "completed_with_warnings",
          str(result.get("status")))
    check("engine returns plan", "plan" in result, str(result.keys()))
    check("engine returns summary", "summary" in result)
    check("summary has task_type",
          result["summary"].get("task_type") == "bug_fix",
          result["summary"].get("task_type", "N/A"))
    check("summary has agents_selected",
          len(result["summary"].get("agents_selected", [])) > 0,
          str(result["summary"].get("agents_selected")))
    check("decision_id present",
          bool(result.get("decision_id")), str(result.get("decision_id")))
    check("mode is build", result.get("mode") == "build")

    plan = result.get("plan", {})
    check("plan has tasks",
          len(plan.get("tasks", [])) > 0,
          str(len(plan.get("tasks", []))))
    check("plan has classification",
          plan.get("classification", {}).get("task_type") == "bug_fix",
          str(plan.get("classification")))
    check("plan has model info",
          plan.get("model", {}).get("primary") is not None,
          str(plan.get("model")))
    check("plan has skills",
          "skills" in plan, str(list(plan.keys())))

    check("dispatched has architect",
          "architect" in runtime_engine._dispatched,
          str(list(runtime_engine._dispatched.keys())))
    check("dispatched has coder",
          "coder" in runtime_engine._dispatched)
    check("dispatched has tester",
          "tester" in runtime_engine._dispatched)
    check("dispatched has reviewer",
          "reviewer" in runtime_engine._dispatched)

    check("history has entry",
          len(runtime_engine.history()) >= 1)
    hist_entry = runtime_engine.history(1)[0]
    check("history entry has task",
          "fix edge case" in hist_entry.get("task", ""))

def test_engine_with_complex_task():
    runtime_engine._dispatched.clear()
    req = DecisionRequest(
        task="Implement user authentication module with JWT tokens",
        context={"project_type": "webapp", "language": "python"},
        source="test",
        mode=EnvironmentMode.BUILD,
    )
    result = runtime_engine.decide(req)

    check("complex task returns completed_or_warning",
          result.get("status") in ("completed", "completed_with_warnings"),
          str(result.get("status")))
    plan = result.get("plan", {})
    check("complex plan has >= 4 tasks",
          len(plan.get("tasks", [])) >= 4,
          str(len(plan.get("tasks", []))))
    check("complex plan classification is feature",
          plan.get("classification", {}).get("task_type") == "feature",
          str(plan.get("classification")))

def test_engine_simple_task_no_approval():
    runtime_engine._dispatched.clear()
    req = DecisionRequest(
        task="Fix typo in README file",
        context={}, source="test", mode=EnvironmentMode.BUILD,
        skip_approvals=True,
    )
    result = runtime_engine.decide(req)
    check("simple task completes",
          result.get("status") in ("completed", "completed_with_warnings"),
          str(result.get("status")))
    plan = result.get("plan", {})
    check("simple plan has tasks",
          len(plan.get("tasks", [])) > 0)

def test_engine_mode_propagation():
    for mode in (EnvironmentMode.TEACHING, EnvironmentMode.AUTONOMOUS):
        runtime_engine._dispatched.clear()
        req = DecisionRequest(task="test", context={}, source="test", mode=mode, skip_approvals=True)
        result = runtime_engine.decide(req)
        check(f"mode {mode.value} propagates", result.get("mode") == mode.value,
              f"got {result.get('mode')}")
        prio = result.get("priorities", [])
        check(f"mode {mode.value} has priorities", len(prio) > 0, str(prio))

def test_engine_validation_block():
    runtime_engine._dispatched.clear()
    runtime_engine._dispatched["coder"] = {"status": "error", "error": "simulated"}
    req = DecisionRequest(task="x", context={}, source="test", mode=EnvironmentMode.BUILD, skip_approvals=True)
    result = runtime_engine.decide(req)
    check("engine tolerates simulated validation block",
          result.get("status") in ("completed_with_warnings", "completed"),
          str(result.get("status")))

if __name__ == "__main__":
    print("=== Runtime Engine Integration Tests ===\n")
    test_runtime_engine_decide_pipeline()
    test_engine_with_complex_task()
    test_engine_simple_task_no_approval()
    test_engine_mode_propagation()
    test_engine_validation_block()
    print(f"\n=== Results: {passed} passed, {failed} failed ===")
    if errors:
        for e in errors:
            print(e)
    sys.exit(0 if failed == 0 else 1)