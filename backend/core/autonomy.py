from typing import Any, Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class AutonomyMode(str, Enum):
    PLAN = "plan"
    AGENT = "agent"
    FULL = "full"


class CapabilityRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalClass(int, Enum):
    NONE = 0
    SESSION = 1
    PROJECT = 2
    EXPLICIT = 3


class CapabilityType(str, Enum):
    PERMANENT = "permanent"
    SESSION = "session"
    TEMPORARY = "temporary"


@dataclass
class Capability:
    name: str
    risk: CapabilityRisk
    approval_class: ApprovalClass
    description: str = ""


ROLE_CAPABILITIES: Dict[str, List[str]] = {
    "planner": ["read_files", "memory_read", "web_research", "documentation_create"],
    "architect": ["read_files", "memory_read", "architecture_documentation", "design_analysis"],
    "coder": ["read_files", "create_files", "write_files", "execute_command", "git_commit", "git_branch_create"],
    "tester": ["read_files", "execute_command", "run_tests", "generate_reports"],
    "reviewer": ["read_files", "analyze_code", "generate_review_reports"],
    "memory": ["memory_read", "memory_write", "memory_update", "memory_compress"],
    "manager": ["workflow_control", "capability_grants", "agent_assignment", "escalation_control", "approval_management"],
}

CAPABILITY_REGISTRY: Dict[str, Capability] = {
    "read_files": Capability("read_files", CapabilityRisk.LOW, ApprovalClass.NONE, "Read files on filesystem"),
    "create_files": Capability("create_files", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Create new files"),
    "write_files": Capability("write_files", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Modify existing files"),
    "delete_files": Capability("delete_files", CapabilityRisk.HIGH, ApprovalClass.SESSION, "Delete files"),
    "execute_command": Capability("execute_command", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Execute shell commands"),
    "run_tests": Capability("run_tests", CapabilityRisk.LOW, ApprovalClass.SESSION, "Run test suites"),
    "build_project": Capability("build_project", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Build project"),
    "install_package": Capability("install_package", CapabilityRisk.HIGH, ApprovalClass.PROJECT, "Install dependencies"),
    "git_status": Capability("git_status", CapabilityRisk.LOW, ApprovalClass.NONE, "Check git status"),
    "git_commit": Capability("git_commit", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Create git commits"),
    "git_branch_create": Capability("git_branch_create", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Create branches"),
    "git_branch_delete": Capability("git_branch_delete", CapabilityRisk.HIGH, ApprovalClass.PROJECT, "Delete branches"),
    "git_push": Capability("git_push", CapabilityRisk.HIGH, ApprovalClass.PROJECT, "Push to remote"),
    "git_pull": Capability("git_pull", CapabilityRisk.LOW, ApprovalClass.NONE, "Pull from remote"),
    "git_merge": Capability("git_merge", CapabilityRisk.CRITICAL, ApprovalClass.EXPLICIT, "Merge branches"),
    "git_tag": Capability("git_tag", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Tag releases"),
    "database_read": Capability("database_read", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Read database"),
    "database_write": Capability("database_write", CapabilityRisk.HIGH, ApprovalClass.PROJECT, "Write to database"),
    "database_migrate": Capability("database_migrate", CapabilityRisk.HIGH, ApprovalClass.EXPLICIT, "Run migrations"),
    "database_delete": Capability("database_delete", CapabilityRisk.CRITICAL, ApprovalClass.EXPLICIT, "Delete database data"),
    "memory_read": Capability("memory_read", CapabilityRisk.LOW, ApprovalClass.NONE, "Read agent memory"),
    "memory_write": Capability("memory_write", CapabilityRisk.LOW, ApprovalClass.SESSION, "Write to agent memory"),
    "memory_update": Capability("memory_update", CapabilityRisk.LOW, ApprovalClass.SESSION, "Update memory entries"),
    "memory_compress": Capability("memory_compress", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Compress memory"),
    "web_research": Capability("web_research", CapabilityRisk.LOW, ApprovalClass.NONE, "Browse web"),
    "workflow_control": Capability("workflow_control", CapabilityRisk.HIGH, ApprovalClass.SESSION, "Control workflows"),
    "capability_grants": Capability("capability_grants", CapabilityRisk.CRITICAL, ApprovalClass.EXPLICIT, "Grant capabilities"),
    "agent_assignment": Capability("agent_assignment", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Assign agents"),
    "escalation_control": Capability("escalation_control", CapabilityRisk.MEDIUM, ApprovalClass.SESSION, "Control escalations"),
    "approval_management": Capability("approval_management", CapabilityRisk.HIGH, ApprovalClass.PROJECT, "Manage approvals"),
    "documentation_create": Capability("documentation_create", CapabilityRisk.LOW, ApprovalClass.NONE, "Create documentation"),
    "architecture_documentation": Capability("architecture_documentation", CapabilityRisk.LOW, ApprovalClass.NONE, "Document architecture"),
    "design_analysis": Capability("design_analysis", CapabilityRisk.LOW, ApprovalClass.NONE, "Analyze designs"),
    "analyze_code": Capability("analyze_code", CapabilityRisk.LOW, ApprovalClass.NONE, "Review code"),
    "generate_reports": Capability("generate_reports", CapabilityRisk.LOW, ApprovalClass.NONE, "Generate reports"),
    "generate_review_reports": Capability("generate_review_reports", CapabilityRisk.LOW, ApprovalClass.NONE, "Review reports"),
    "deploy_staging": Capability("deploy_staging", CapabilityRisk.HIGH, ApprovalClass.PROJECT, "Deploy to staging"),
    "deploy_production": Capability("deploy_production", CapabilityRisk.CRITICAL, ApprovalClass.EXPLICIT, "Deploy to production"),
}


class PermissionManager:
    def __init__(self):
        self.session_approvals: Dict[str, bool] = {}
        self.project_approvals: Dict[str, bool] = {}
        self.grant_log: List[Dict] = []

    def get_role_capabilities(self, role: str) -> List[str]:
        return ROLE_CAPABILITIES.get(role, ["read_files", "memory_read"])

    def get_capability_risk(self, capability: str) -> CapabilityRisk:
        cap = CAPABILITY_REGISTRY.get(capability)
        return cap.risk if cap else CapabilityRisk.MEDIUM

    def check_action_allowed(self, action: str, role: str, mode: AutonomyMode) -> Dict:
        cap = CAPABILITY_REGISTRY.get(action)
        role_caps = self.get_role_capabilities(role)

        if mode == AutonomyMode.PLAN:
            if action in ("read_files", "memory_read", "web_research", "documentation_create",
                          "architecture_documentation", "design_analysis", "analyze_code",
                          "generate_reports", "generate_review_reports"):
                return {"allowed": True, "reason": "Plan mode read action"}
            return {"allowed": False, "reason": f"Action '{action}' not allowed in PLAN mode",
                    "allowed_in": ["agent", "full"]}

        if action not in role_caps:
            return {"allowed": False, "reason": f"Role '{role}' lacks capability '{action}'",
                    "required_role": next((r for r, caps in ROLE_CAPABILITIES.items() if action in caps), None)}

        risk = self.get_capability_risk(action)
        if mode == AutonomyMode.AGENT and risk in (CapabilityRisk.HIGH, CapabilityRisk.CRITICAL):
            return {"allowed": True, "reason": f"Action allowed in AGENT mode",
                    "warnings": [f"High-risk action '{action}' requires approval"],
                    "approval_required": cap.approval_class.value if cap else ApprovalClass.EXPLICIT.value}

        return {"allowed": True, "reason": f"Action allowed in {mode.value} mode"}


class ApprovalManager:
    def __init__(self):
        self.session_grants: Dict[str, Set[str]] = {}
        self.project_grants: Dict[str, Set[str]] = {}
        self.audit_log: List[Dict] = []

    def grant_session(self, session_id: str, capabilities: List[str]) -> Dict:
        self.session_grants.setdefault(session_id, set()).update(capabilities)
        entry = {"type": "session", "session_id": session_id, "capabilities": capabilities,
                 "timestamp": datetime.utcnow().isoformat()}
        self.audit_log.append(entry)
        return entry

    def grant_project(self, project_id: str, capabilities: List[str]) -> Dict:
        self.project_grants.setdefault(project_id, set()).update(capabilities)
        entry = {"type": "project", "project_id": project_id, "capabilities": capabilities,
                 "timestamp": datetime.utcnow().isoformat()}
        self.audit_log.append(entry)
        return entry

    def check_approval(self, action: str, session_id: str, project_id: str = "") -> Dict:
        cap = CAPABILITY_REGISTRY.get(action)
        if not cap:
            return {"approved": True, "reason": "Unknown action"}

        if cap.approval_class == ApprovalClass.NONE:
            return {"approved": True, "reason": "No approval required"}

        if cap.approval_class == ApprovalClass.SESSION:
            approved = session_id in self.session_grants and action in self.session_grants[session_id]
            return {"approved": approved, "reason": "Session approval" if approved else "Session approval required"}

        if cap.approval_class == ApprovalClass.PROJECT:
            if not project_id:
                return {"approved": False, "reason": "Project approval required"}
            approved = project_id in self.project_grants and action in self.project_grants[project_id]
            return {"approved": approved, "reason": "Project approval" if approved else "Project approval required"}

        return {"approved": False, "reason": "Explicit approval always required"}

    def revoke_session(self, session_id: str) -> Dict:
        caps = list(self.session_grants.get(session_id, set()))
        self.session_grants.pop(session_id, None)
        entry = {"type": "revoke_session", "session_id": session_id, "capabilities": caps,
                 "timestamp": datetime.utcnow().isoformat()}
        self.audit_log.append(entry)
        return entry

    def revoke_project(self, project_id: str) -> Dict:
        caps = list(self.project_grants.get(project_id, set()))
        self.project_grants.pop(project_id, None)
        entry = {"type": "revoke_project", "project_id": project_id, "capabilities": caps,
                 "timestamp": datetime.utcnow().isoformat()}
        self.audit_log.append(entry)
        return entry

    def get_audit_log(self, limit: int = 20) -> List[Dict]:
        return self.audit_log[-limit:]


class AutonomyController:
    def __init__(self):
        self.mode: AutonomyMode = AutonomyMode.AGENT
        self.permissions = PermissionManager()
        self.approvals = ApprovalManager()
        self.decisions: List[Dict] = []

    def set_mode(self, mode: AutonomyMode) -> Dict:
        old = self.mode
        self.mode = mode
        result = {"previous_mode": old.value, "current_mode": mode.value,
                  "timestamp": datetime.utcnow().isoformat()}
        self.decisions.append(result)
        return result

    def can_execute(self, action: str, role: str, session_id: str,
                    project_id: str = "", confidence: str = "medium") -> Dict:
        perm = self.permissions.check_action_allowed(action, role, self.mode)
        if not perm["allowed"]:
            return {"can_execute": False, "permission": perm}

        appr = self.approvals.check_approval(action, session_id, project_id)
        if not appr["approved"]:
            return {"can_execute": False, "permission": perm, "approval": appr}

        confidence_thresholds = {"high": 0.7, "medium": 0.8, "low": 0.95}
        conf_scores = {"high": 0.9, "medium": 0.7, "low": 0.5}
        risk = self.permissions.get_capability_risk(action)

        risk_multipliers = {"low": 1.0, "medium": 1.1, "high": 1.3, "critical": 1.5}
        threshold = confidence_thresholds.get(confidence, 0.8)
        risk_factor = risk_multipliers.get(risk.value, 1.0)
        effective_threshold = min(threshold * risk_factor, 1.0)
        agent_confidence = conf_scores.get(confidence, 0.7)

        if agent_confidence < effective_threshold:
            return {"can_execute": True,
                    "permission": perm, "approval": appr,
                    "warnings": [f"Confidence ({confidence}) may be insufficient for risk level ({risk.value})"],
                    "recommend": "escalate"}

        return {"can_execute": True, "permission": perm, "approval": appr, "warnings": perm.get("warnings", [])}
