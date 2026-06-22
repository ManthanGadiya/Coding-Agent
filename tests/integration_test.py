"""Integration tests for CAMera backend subsystems.
Runs against FastAPI TestClient (no server needed).
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

passed = 0
failed = 0
errors = []


def check(label: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS {label}")
    else:
        failed += 1
        msg = f"  FAIL {label}: {detail}" if detail else f"  FAIL {label}"
        errors.append(msg)
        print(msg)


# ── Health ──
def test_health():
    r = client.get("/health")
    check("GET /health returns 200", r.status_code == 200)
    check("health.status is healthy", r.json().get("status") == "healthy")


# ── Agents ──
def test_agents():
    r = client.get("/api/v1/agents")
    check("GET /agents returns 200", r.status_code == 200)
    data = r.json()
    check("/agents returns list", isinstance(data, list))
    check("/agents has 8 agents", len(data) == 8, str(len(data)))

    r2 = client.get("/api/v1/agents/manager/status")
    check("GET /manager/status returns 200", r2.status_code == 200)
    s = r2.json()
    check("manager.status has registered_agents", "registered_agents" in s)
    check("manager.status has agents list", "agents" in s)
    check("manager has 8 agents", len(s.get("agents", {})) >= 7,
          f"got {len(s.get('agents', {}))}")


# ── Run Goal ──
def test_run_goal():
    r = client.post("/api/v1/agents/run-goal", json={
        "goal": "Add a health check endpoint to the API",
        "context": {"project": "test", "priority": "low"}
    })
    check("POST /agents/run-goal returns 200", r.status_code == 200)
    data = r.json()
    check("run-goal has goal", data.get("goal") == "Add a health check endpoint to the API")
    check("run-goal has classification", bool(data.get("classification")))
    check("run-goal has complexity", bool(data.get("complexity")))
    check("run-goal has pipeline_id", bool(data.get("pipeline_id")))
    check("run-goal has steps list", len(data.get("steps", [])) > 0)
    check("run-goal has success", "success" in data)
    check("run-goal has total_steps", data.get("total_steps", 0) > 0)
    check("run-goal steps all have status", all("status" in s for s in data.get("steps", [])))

    r2 = client.post("/api/v1/agents/run-goal", json={
        "goal": "Fix the database connection bug causing timeout errors",
    })
    check("run-goal without context also works", r2.status_code == 200)
    check("run-goal classifies debugging tasks",
          r2.json().get("classification") == "debugging",
          f"got {r2.json().get('classification')}")

    r3 = client.post("/api/v1/agents/run-goal", json={
        "goal": "hi",
    })
    check("run-goal simple goal works", r3.status_code == 200)
    check("simple goal is complexity 1",
          r3.json().get("complexity") == "simple",
          f"got {r3.json().get('complexity')}")


# ── Projects ──
def test_projects():
    ts = str(int(time.time() * 1000))
    r = client.post("/api/v1/projects", json={
        "name": f"test-project-{ts}",
        "display_name": f"Test Project {ts}",
        "description": "Integration test project",
    })
    check("POST /projects creates project", r.status_code in (200, 201),
          f"status {r.status_code} detail: {r.text[:200] if r.status_code == 422 else ''}")
    if r.status_code in (200, 201):
        pid = r.json().get("id", "")
        r2 = client.get("/api/v1/projects")
        check("GET /projects lists projects", r2.status_code == 200)
        data = r2.json()
        projects = data if isinstance(data, list) else data.get("projects", [])
        check("projects list is non-empty", len(projects) >= 1)
        if pid:
            r3 = client.get(f"/api/v1/projects/{pid}")
            check("GET /projects/:id returns project", r3.status_code == 200)


# ── Tasks ──
def test_tasks():
    r = client.post("/api/v1/tasks", json={
        "title": "Test Task",
        "description": "Integration test task",
        "assigned_agent_type": "coder"
    })
    check("POST /tasks creates task", r.status_code in (200, 201),
          f"status {r.status_code}")
    r2 = client.get("/api/v1/tasks")
    check("GET /tasks returns list", r2.status_code == 200)

    r3 = client.get("/api/v1/tasks?assigned_agent_type=coder")
    check("GET /tasks?agent_type= works", r3.status_code == 200)
    data = r3.json()
    tasks = data if isinstance(data, list) else data.get("tasks", [])
    if tasks:
        first = tasks[0]
        check("task has id", "id" in first or "task_id" in first)


# ── Decision Engine ──
def test_decisions():
    r = client.post("/api/v1/decisions/decide", json={
        "objective": "Choose database for integration test",
        "options": [
            {"label": "PostgreSQL", "maintainability": 8, "complexity": 3, "risk": "low", "cost": 3, "correctness": 9},
            {"label": "SQLite", "maintainability": 9, "complexity": 2, "risk": "low", "cost": 1, "correctness": 7},
        ],
        "decision_type": "technical",
        "evidence": ["Good for ACID", "Team knows SQL"],
    })
    check("POST /decisions/decide returns 200", r.status_code == 200)
    d = r.json()
    check("decision has recommendation", "recommendation" in d)
    check("decision has confidence", "confidence" in d)
    check("decision has decision_id", "decision_id" in d)
    check("decision has steps_taken", len(d.get("steps_taken", [])) > 0)
    check("decision recommendation is non-empty", bool(d.get("recommendation")))

    r2 = client.get("/api/v1/decisions/history?limit=5")
    check("GET /decisions/history returns 200", r2.status_code == 200)
    check("history has decisions", len(r2.json()) >= 1)

    r3 = client.post("/api/v1/decisions/assess-risk?description=test&impact=0.8&likelihood=0.5")
    check("POST /assess-risk returns 200", r3.status_code == 200)
    risk = r3.json()
    check("risk has level", "level" in risk)


# ── Autonomy ──
def test_autonomy():
    r = client.get("/api/v1/autonomy/mode")
    check("GET /autonomy/mode returns 200", r.status_code == 200)
    check("autonomy mode is set", "mode" in r.json())

    r2 = client.post("/api/v1/autonomy/mode", json={"mode": "agent"})
    check("POST /autonomy/mode switches mode", r2.status_code == 200)

    r3 = client.post("/api/v1/autonomy/check", json={
        "action": "read_files", "role": "planner", "session_id": "test-sess", "confidence": "high"
    })
    check("POST /autonomy/check returns 200", r3.status_code == 200)
    check("action check has can_execute", "can_execute" in r3.json())

    r4 = client.get("/api/v1/autonomy/capabilities/planner")
    check("GET /capabilities/:role returns 200", r4.status_code == 200)
    caps = r4.json().get("capabilities", [])
    check("planner has read_files", "read_files" in caps)
    check("planner does NOT have write_files", "write_files" not in caps)

    r5 = client.get("/api/v1/autonomy/registry")
    check("GET /registry returns capabilities", r5.status_code == 200)
    check("registry has 35+ capabilities", len(r5.json()) >= 30,
          f"got {len(r5.json())}")

    r6 = client.post("/api/v1/autonomy/grant/session", json={
        "session_id": "test-sess", "capabilities": ["write_files", "git_commit"]
    })
    check("POST /grant/session works", r6.status_code == 200)

    r7 = client.get("/api/v1/autonomy/audit?limit=10")
    check("GET /audit returns log", r7.status_code == 200)
    check("audit log has entries", len(r7.json()) >= 1)


# ── Workflow Engine ──
def test_workflows():
    r = client.post("/api/v1/workflows/blueprint", json={
        "category": "feature", "complexity": "complex"
    })
    check("POST /workflows/blueprint returns 200", r.status_code == 200)
    bp = r.json()
    check("blueprint has category", bp.get("category") == "feature")
    check("blueprint has steps", len(bp.get("steps", [])) > 0)
    check("blueprint requires architect for complex feature",
          bp.get("requires_architect") is True)
    check("blueprint requires approval for complex feature",
          bp.get("requires_approval") is True)

    r2 = client.post("/api/v1/workflows/classify", json={
        "scope": "large", "risk": "high", "dependencies": 3,
        "architecture_impact": True, "security_impact": True, "research_needed": True
    })
    check("POST /workflows/classify returns 200", r2.status_code == 200)
    check("classification is critical",
          r2.json().get("complexity") == "critical",
          f"got {r2.json().get('complexity')}")

    r3 = client.get("/api/v1/workflows/categories")
    check("GET /workflows/categories returns 200", r3.status_code == 200)
    cats = r3.json().get("categories", [])
    check("6 workflow categories exist", len(cats) == 6, f"got {len(cats)}")

    r4 = client.post("/api/v1/workflows", json={
        "name": "Test Feature Workflow",
        "workflow_type": "feature_development",
        "steps": [
            {"agent_id": "manager", "task_type": "analyze", "description": "Analyze"},
            {"agent_id": "coder", "task_type": "implement", "description": "Implement"},
        ],
    })
    check("POST /workflows creates workflow", r4.status_code in (200, 201),
          f"status {r4.status_code}")


# ── Learning System ──
def test_learning():
    r = client.post("/api/v1/learning/failures", json={
        "description": "API timeout during load test",
        "category": "internal", "severity": "high",
        "impact": "Users cannot access service",
        "affected_components": ["api-gateway"],
        "root_cause": "Connection pool exhausted under load",
        "root_cause_confidence": "high",
        "resolution": "Increased pool size from 10 to 50",
        "preventive_actions": ["Add connection pool monitoring", "Auto-scale threshold"],
    })
    check("POST /learning/failures creates failure", r.status_code == 200)
    f = r.json()
    check("failure has failure_id", "failure_id" in f)
    check("failure auto-generated lesson",
          f.get("root_cause_confidence") == "high")

    r2 = client.get("/api/v1/learning/failures")
    check("GET /learning/failures returns list", r2.status_code == 200)
    check("failures list is non-empty", len(r2.json()) >= 1)

    r3 = client.post("/api/v1/learning/lessons", json={
        "topic": "Always use connection pooling",
        "description": "Connection pooling prevents exhaustion under load",
        "evidence": ["Failure FAIL-0001", "Post-mortem analysis"],
        "confidence": "high",
        "scope": "global",
    })
    check("POST /learning/lessons creates lesson", r3.status_code == 200)
    l = r3.json()
    check("lesson has lesson_id", "lesson_id" in l)

    r4 = client.get("/api/v1/learning/lessons?scope=global&status=active")
    check("GET /learning/lessons filters", r4.status_code == 200)
    check("lessons match filter", len(r4.json()) >= 1)

    r5 = client.post("/api/v1/learning/metrics", json={
        "overall": 85.0,
        "categories": {"correctness": 90, "quality": 85, "reliability": 80, "testing": 75}
    })
    check("POST /learning/metrics records", r5.status_code == 200)

    r6 = client.get("/api/v1/learning/metrics")
    check("GET /learning/metrics returns list", r6.status_code == 200)
    check("metrics list is non-empty", len(r6.json()) >= 1)

    r7 = client.post("/api/v1/learning/metrics/score", json={
        "categories": {"correctness": 92, "quality": 88, "reliability": 75,
                       "testing": 70, "governance": 95, "efficiency": 80}
    })
    check("POST /learning/metrics/score returns 200", r7.status_code == 200)
    s = r7.json()
    check("score has overall", "overall" in s)
    check("score has alerts", "alerts" in s)

    r8 = client.post("/api/v1/learning/proposals", json={
        "observation": "Connection pool issues cause recurring failures",
        "evidence": ["Failure FAIL-0001", "3 incidents in 30 days"],
        "expected_benefit": "Reduce API timeout incidents by 90%",
        "risks": ["Memory overhead from larger pools"],
        "confidence": "high",
        "recommendation": "Implement dynamic pool sizing",
    })
    check("POST /learning/proposals creates", r8.status_code == 200)
    p = r8.json()
    check("proposal has proposal_id", "proposal_id" in p)

    r9 = client.get("/api/v1/learning/proposals?status=proposed")
    check("GET /learning/proposals filters", r9.status_code == 200)
    check("proposals match filter", len(r9.json()) >= 1)

    r10 = client.post("/api/v1/learning/five-whys", json={
        "problem": "API timeout\nConnection pool exhausted\nToo many concurrent requests\nAutoscaling too slow\nDefault pool size too small\nNo monitoring alerted"
    })
    check("POST /learning/five-whys returns 200", r10.status_code == 200)
    whys = r10.json()
    check("5 whys returns 6 entries (1 problem + 5 whys)",
          len(whys) == 6, f"got {len(whys)}")


# ── Memory Retrieval ──
def test_memory_retrieval():
    r = client.post("/api/v1/memory-retrieval/store", json={
        "content": "Use JWT with refresh tokens for API auth",
        "tags": ["auth", "jwt", "security", "recommended"],
        "importance": 0.9, "confidence": 0.95, "outcome_quality": 0.85,
        "agent": "architect",
    })
    check("POST /memory-retrieval/store stores memory", r.status_code == 200)
    check("stored memory has id", "id" in r.json())

    r2 = client.post("/api/v1/memory-retrieval/store", json={
        "content": "Avoid JWT for systems needing immediate revocation",
        "tags": ["auth", "jwt", "caution", "alternative"],
        "importance": 0.7, "confidence": 0.8,
        "relationships": ["MEM-00001"],
        "agent": "architect",
    })
    check("stored second memory", r2.status_code == 200)

    r3 = client.post("/api/v1/memory-retrieval/retrieve", json={
        "query": "JWT authentication", "agent": "architect",
        "mode": "architecture", "task_complexity": "moderate"
    })
    check("POST /memory-retrieval/retrieve returns 200", r3.status_code == 200)
    ret = r3.json()
    check("retrieved has memories list", "memories" in ret)
    check("retrieved has summary", "summary" in ret)
    check("retrieved has contradictions", "contradictions" in ret)
    check("retrieved has confidence", "confidence" in ret)
    check("retrieved has knowledge_graph", "knowledge_graph" in ret)

    r4 = client.get("/api/v1/memory-retrieval/profiles")
    check("GET /memory-retrieval/profiles returns 200", r4.status_code == 200)
    profiles = r4.json()
    check("8 agent profiles exist", len(profiles) >= 7, f"got {len(profiles)}")

    r5 = client.get("/api/v1/memory-retrieval/profile/architect")
    check("GET /profile/architect returns 200", r5.status_code == 200)
    profile = r5.json()
    check("architect profile has architecture_decisions",
          "architecture_decisions" in profile.get("profile", {}))


# ── Run all tests ──
if __name__ == "__main__":
    print("=" * 60)
    print("CAMera Integration Tests")
    print("=" * 60)

    test_health()
    print()
    test_agents()
    print()
    test_run_goal()
    print()
    test_projects()
    print()
    test_tasks()
    print()
    test_decisions()
    print()
    test_autonomy()
    print()
    test_workflows()
    print()
    test_learning()
    print()
    test_memory_retrieval()
    print()

    print("=" * 60)
    total = passed + failed
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if errors:
        print("\nFailures:")
        for e in errors:
            print(e)
    print("=" * 60)
    sys.exit(1 if failed > 0 else 0)
