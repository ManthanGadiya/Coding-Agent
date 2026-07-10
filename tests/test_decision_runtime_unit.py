import pytest
from backend.decision_runtime.task_classifier import task_classifier, TaskType, TASK_KEYWORDS
from backend.decision_runtime.state_machine import state_machine, RuntimeState, StateMachine
from backend.decision_runtime.approval_manager import approval_manager, ApprovalScope, ApprovalStatus
from backend.decision_runtime.registries import BaseRegistry, AgentCapability, SkillDef, MCPDef, ModelDef


class TestTaskClassifier:
    def test_classify_bug_fix(self):
        r = task_classifier.classify("Fix the broken login crash error")
        assert r.task_type == TaskType.BUG_FIX
        assert r.confidence > 0.5
        assert r.keywords

    def test_classify_feature(self):
        r = task_classifier.classify("Add a new dashboard feature")
        assert r.task_type == TaskType.FEATURE

    def test_classify_research(self):
        r = task_classifier.classify("Research alternatives for the database layer")
        assert r.task_type == TaskType.RESEARCH

    def test_classify_refactor(self):
        r = task_classifier.classify("Clean up and rewrite the legacy payment processing code")
        assert r.task_type == TaskType.REFACTOR

    def test_classify_general_fallback(self):
        r = task_classifier.classify("Do something")
        assert r.task_type == TaskType.GENERAL
        assert r.confidence < 0.5

    def test_classify_complexity_critical(self):
        r = task_classifier.classify("Critical urgent emergency large complex task " * 10)
        assert r.complexity == "critical"
        assert r.risk == "high"

    def test_classify_complexity_simple(self):
        r = task_classifier.classify("A quick simple trivial task")
        assert r.complexity == "simple"

    def test_classify_with_title(self):
        r = task_classifier.classify("fix something", title="BUG REPORT: Login broken")
        assert r.task_type == TaskType.BUG_FIX

    def test_classify_large_project_effort(self):
        r = task_classifier.classify("Large multi-stage complex platform initiative")
        assert r.estimated_effort == "large"

    def test_keywords_all_have_entries(self):
        exclude = {TaskType.GENERAL}
        for task_type in TaskType:
            if task_type in exclude:
                continue
            assert task_type in TASK_KEYWORDS, f"Missing keywords for {task_type}"


class TestStateMachine:
    def test_create_instance(self):
        sm = StateMachine()
        inst = sm.create("test-1")
        assert inst.current_state == RuntimeState.RECEIVED
        assert inst.instance_id == "test-1"

    def test_valid_transition(self):
        sm = StateMachine()
        inst = sm.create("test-2")
        result = sm.transition("test-2", RuntimeState.CLASSIFYING)
        assert result.current_state == RuntimeState.CLASSIFYING
        assert len(result.transitions) == 1

    def test_invalid_transition_raises(self):
        sm = StateMachine()
        sm.create("test-3")
        with pytest.raises(ValueError, match="Cannot transition"):
            sm.transition("test-3", RuntimeState.COMPLETED)

    def test_nonexistent_instance_returns_none(self):
        sm = StateMachine()
        assert sm.transition("nope", RuntimeState.CLASSIFYING) is None

    def test_can_transition(self):
        sm = StateMachine()
        sm.create("test-4")
        assert sm.can_transition("test-4", RuntimeState.CLASSIFYING) is True
        assert sm.can_transition("test-4", RuntimeState.COMPLETED) is False

    def test_get_state(self):
        sm = StateMachine()
        sm.create("test-5")
        assert sm.get_state("test-5") == RuntimeState.RECEIVED
        assert sm.get_state("nope") is None

    def test_list_active_excludes_terminal(self):
        sm = StateMachine()
        sm.create("active-1")
        sm.create("active-2")
        sm.create("done")
        sm.transition("done", RuntimeState.CLASSIFYING)
        sm.transition("done", RuntimeState.MEMORY_LOADING)
        sm.transition("done", RuntimeState.CORE_DECISION)
        sm.transition("done", RuntimeState.AGENT_SELECTION)
        sm.transition("done", RuntimeState.SKILL_SELECTION)
        sm.transition("done", RuntimeState.MCP_SELECTION)
        sm.transition("done", RuntimeState.MODEL_SELECTION)
        sm.transition("done", RuntimeState.APPROVAL_CHECK)
        sm.transition("done", RuntimeState.RESEARCHING)
        sm.transition("done", RuntimeState.ARCHITECTING)
        sm.transition("done", RuntimeState.PLANNING)
        sm.transition("done", RuntimeState.APPROVING)
        sm.transition("done", RuntimeState.IMPLEMENTING)
        sm.transition("done", RuntimeState.TESTING)
        sm.transition("done", RuntimeState.REVIEWING)
        sm.transition("done", RuntimeState.DOCUMENTING)
        sm.transition("done", RuntimeState.VALIDATING)
        sm.transition("done", RuntimeState.MEMORY_UPDATING)
        sm.transition("done", RuntimeState.COMPLETED)
        active = sm.list_active()
        ids = [i.instance_id for i in active]
        assert "active-1" in ids
        assert "done" not in ids

    def test_remove(self):
        sm = StateMachine()
        sm.create("test-6")
        sm.remove("test-6")
        assert sm.get("test-6") is None

    def test_transition_to_completed_sets_completed_at(self):
        sm = StateMachine()
        sm.create("test-7")
        for s in [RuntimeState.CLASSIFYING, RuntimeState.MEMORY_LOADING,
                   RuntimeState.CORE_DECISION, RuntimeState.AGENT_SELECTION,
                   RuntimeState.SKILL_SELECTION, RuntimeState.MCP_SELECTION,
                   RuntimeState.MODEL_SELECTION, RuntimeState.APPROVAL_CHECK,
                   RuntimeState.RESEARCHING, RuntimeState.ARCHITECTING,
                   RuntimeState.PLANNING, RuntimeState.APPROVING,
                   RuntimeState.IMPLEMENTING, RuntimeState.TESTING,
                   RuntimeState.REVIEWING, RuntimeState.DOCUMENTING,
                   RuntimeState.VALIDATING, RuntimeState.MEMORY_UPDATING]:
            sm.transition("test-7", s)
        sm.transition("test-7", RuntimeState.COMPLETED)
        inst = sm.get("test-7")
        assert inst.completed_at is not None

    def test_full_pipeline_transition(self):
        sm = StateMachine()
        sm.create("pipeline")
        path = [RuntimeState.CLASSIFYING, RuntimeState.MEMORY_LOADING,
                RuntimeState.CORE_DECISION, RuntimeState.AGENT_SELECTION,
                RuntimeState.SKILL_SELECTION, RuntimeState.MCP_SELECTION,
                RuntimeState.MODEL_SELECTION, RuntimeState.APPROVAL_CHECK,
                RuntimeState.RESEARCHING, RuntimeState.ARCHITECTING,
                RuntimeState.PLANNING, RuntimeState.APPROVING,
                RuntimeState.IMPLEMENTING, RuntimeState.TESTING,
                RuntimeState.REVIEWING, RuntimeState.DOCUMENTING,
                RuntimeState.VALIDATING, RuntimeState.MEMORY_UPDATING,
                RuntimeState.COMPLETED]
        for s in path:
            sm.transition("pipeline", s)
        assert sm.get_state("pipeline") == RuntimeState.COMPLETED


class TestApprovalManager:
    def test_request_approval(self):
        req = approval_manager.request(ApprovalScope.RELEASE, "Need approval",
                                        data={}, requested_by="tester")
        assert req.scope == ApprovalScope.RELEASE
        assert req.status == ApprovalStatus.PENDING

    def test_approve(self):
        req = approval_manager.request(ApprovalScope.DEPLOYMENT, "Approve deploy",
                                        data={}, requested_by="tester")
        pending = approval_manager.get_pending()
        rid = list(pending.keys())[0]
        result = approval_manager.respond(rid, approved=True, by="manager", response="Looks good")
        assert result.status == ApprovalStatus.APPROVED
        assert result.approved_by == "manager"

    def test_reject(self):
        req = approval_manager.request(ApprovalScope.STRATEGIC_DECISION, "Reject strategic",
                                        data={}, requested_by="tester")
        pending = approval_manager.get_pending()
        rid = list(pending.keys())[0]
        result = approval_manager.respond(rid, approved=False, by="manager", response="Not ready")
        assert result.status == ApprovalStatus.REJECTED

    def test_respond_nonexistent(self):
        result = approval_manager.respond("nonexistent", approved=True)
        assert result is None

    def test_pending_list(self):
        approval_manager.request(ApprovalScope.STRATEGIC_DECISION, "Strategic",
                                  data={}, requested_by="tester")
        pending = approval_manager.get_pending()
        assert len(pending) > 0

    def test_check_task_approvals(self):
        from backend.decision_runtime.task_classifier import TaskType
        scopes = approval_manager.check_task_approvals(TaskType.DEPLOYMENT, "complex")
        assert ApprovalScope.DEPLOYMENT in scopes
        assert ApprovalScope.RELEASE in scopes


class TestBaseRegistry:
    def test_register_and_get(self):
        r = BaseRegistry()
        cap = AgentCapability(agent_type="test", display_name="Test",
                               capabilities=["code"], permissions=["read"],
                               allowed_tools=["read"], models=["small"])
        r.register("test", cap)
        assert r.get("test") is cap

    def test_list_enabled_only(self):
        r = BaseRegistry()
        r.register("a", AgentCapability(agent_type="a", display_name="A",
                                         capabilities=[], permissions=[],
                                         allowed_tools=[], models=[], enabled=True))
        r.register("b", AgentCapability(agent_type="b", display_name="B",
                                         capabilities=[], permissions=[],
                                         allowed_tools=[], models=[], enabled=False))
        assert len(r.list()) == 1
        assert len(r.list(enabled_only=False)) == 2

    def test_find_by_attribute(self):
        r = BaseRegistry()
        r.register("a", SkillDef(name="skill-a", description="First",
                                  activate_conditions=[], task_types=["code"],
                                  required_agents=["coder"], required_mcps=[]))
        r.register("b", SkillDef(name="skill-b", description="Second",
                                  activate_conditions=[], task_types=["review"],
                                  required_agents=["reviewer"], required_mcps=[]))
        results = r.find(task_types=["code"])
        assert len(results) == 1
        assert results[0].name == "skill-a"

    def test_remove(self):
        r = BaseRegistry()
        r.register("x", "value")
        r.remove("x")
        assert r.get("x") is None

    def test_clear(self):
        r = BaseRegistry()
        r.register("a", 1)
        r.register("b", 2)
        r.clear()
        assert len(r.list(enabled_only=False)) == 0

    def test_get_nonexistent(self):
        r = BaseRegistry()
        assert r.get("nonexistent") is None

    def test_find_empty(self):
        r = BaseRegistry()
        assert r.find(name="nothing") == []
