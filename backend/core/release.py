from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ReleaseType(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


class ReleaseState(str, Enum):
    DRAFT = "draft"
    CANDIDATE = "candidate"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class RollbackStrategy:
    method: str
    steps: List[str] = field(default_factory=list)
    validation: List[str] = field(default_factory=list)
    estimated_duration: str = "5m"
    auto_rollback: bool = False


ROLLBACK_STRATEGIES = {
    "git_revert": RollbackStrategy(
        method="git_revert",
        steps=["Create git revert commit", "Push revert to production branch", "Verify no regression"],
        validation=["Tests pass on reverted code", "No data loss confirmed"],
        estimated_duration="10m",
        auto_rollback=True,
    ),
    "db_rollback": RollbackStrategy(
        method="db_rollback",
        steps=["Run down migration", "Restore previous schema", "Verify data integrity"],
        validation=["Data integrity verified", "Schema matches pre-release state"],
        estimated_duration="15m",
        auto_rollback=False,
    ),
    "feature_flag": RollbackStrategy(
        method="feature_flag",
        steps=["Disable feature flag", "Clear cached feature state", "Restore previous behavior"],
        validation=["Feature disabled", "Users see previous behavior"],
        estimated_duration="1m",
        auto_rollback=True,
    ),
    "full_rollback": RollbackStrategy(
        method="full_rollback",
        steps=["Restore previous deployment", "Rerun pre-release migrations", "Validate system health"],
        validation=["Deployment restored", "All services healthy", "Data consistent"],
        estimated_duration="20m",
        auto_rollback=True,
    ),
}


@dataclass
class ReleaseCandidate:
    id: str
    version: str
    release_type: ReleaseType
    state: ReleaseState = ReleaseState.DRAFT
    rollback_strategy: Optional[RollbackStrategy] = None
    checks: Dict[str, bool] = field(default_factory=lambda: {
        "tests_passed": False, "review_passed": False,
        "quality_gate_passed": False, "approval_granted": False,
    })
    approved_by: Optional[str] = None
    deployed_at: Optional[str] = None
    rollback_at: Optional[str] = None
    rollback_reason: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""


class ReleaseEngine:
    def __init__(self):
        self.candidates: Dict[str, ReleaseCandidate] = {}

    def _next_id(self) -> str:
        return f"RC-{len(self.candidates) + 1:04d}"

    def create_candidate(self, version: str, release_type: str = "patch") -> ReleaseCandidate:
        now = datetime.utcnow().isoformat()
        rc = ReleaseCandidate(
            id=self._next_id(), version=version,
            release_type=ReleaseType(release_type),
            rollback_strategy=ROLLBACK_STRATEGIES["full_rollback"],
            created_at=now, updated_at=now,
        )
        self.candidates[rc.id] = rc
        return rc

    def approve_candidate(self, candidate_id: str, approved_by: str = "manager") -> Optional[ReleaseCandidate]:
        rc = self.candidates.get(candidate_id)
        if not rc:
            return None
        rc.state = ReleaseState.APPROVED
        rc.approved_by = approved_by
        rc.updated_at = datetime.utcnow().isoformat()
        return rc

    def deploy(self, candidate_id: str) -> Optional[ReleaseCandidate]:
        rc = self.candidates.get(candidate_id)
        if not rc:
            return None
        if rc.state != ReleaseState.APPROVED:
            return rc
        rc.state = ReleaseState.DEPLOYED
        rc.deployed_at = datetime.utcnow().isoformat()
        rc.updated_at = rc.deployed_at
        return rc

    def rollback(self, candidate_id: str, reason: str) -> Optional[ReleaseCandidate]:
        rc = self.candidates.get(candidate_id)
        if not rc:
            return None
        rc.state = ReleaseState.ROLLED_BACK
        rc.rollback_at = datetime.utcnow().isoformat()
        rc.rollback_reason = reason
        rc.updated_at = rc.rollback_at
        return rc

    def set_check(self, candidate_id: str, check_name: str, passed: bool) -> Optional[ReleaseCandidate]:
        rc = self.candidates.get(candidate_id)
        if not rc:
            return None
        if check_name in rc.checks:
            rc.checks[check_name] = passed
        else:
            for key in rc.checks:
                if key.replace("_", "").startswith(check_name.replace("_", "")):
                    rc.checks[key] = passed
                    break
        rc.updated_at = datetime.utcnow().isoformat()
        return rc

    def get_strategies(self) -> Dict[str, Dict]:
        return {k: {"method": v.method, "steps": v.steps, "validation": v.validation,
                     "estimated_duration": v.estimated_duration, "auto_rollback": v.auto_rollback}
                for k, v in ROLLBACK_STRATEGIES.items()}

    def select_strategy(self, candidate_id: str, strategy_name: str) -> Optional[ReleaseCandidate]:
        rc = self.candidates.get(candidate_id)
        if not rc:
            return None
        strategy = ROLLBACK_STRATEGIES.get(strategy_name)
        if not strategy:
            return None
        rc.rollback_strategy = strategy
        rc.updated_at = datetime.utcnow().isoformat()
        return rc

    def get_candidate(self, candidate_id: str) -> Optional[Dict]:
        rc = self.candidates.get(candidate_id)
        if not rc:
            return None
        return {
            "id": rc.id, "version": rc.version, "release_type": rc.release_type.value,
            "state": rc.state.value, "checks": rc.checks,
            "rollback_strategy": {"method": rc.rollback_strategy.method, "steps": rc.rollback_strategy.steps,
                                  "validation": rc.rollback_strategy.validation}
            if rc.rollback_strategy else None,
            "approved_by": rc.approved_by, "deployed_at": rc.deployed_at,
            "rollback_at": rc.rollback_at, "rollback_reason": rc.rollback_reason,
        }


release_engine = ReleaseEngine()
