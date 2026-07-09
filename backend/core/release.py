from typing import Dict, Optional
from datetime import datetime, timezone
from enum import Enum

from backend.core.database import SessionLocal
from backend.models.learning import ReleaseCandidate as ReleaseCandidateModel


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


ROLLBACK_STRATEGIES = {
    "git_revert": {"method": "git_revert", "steps": ["Create git revert commit", "Push revert to production branch", "Verify no regression"], "validation": ["Tests pass", "No data loss"], "estimated_duration": "10m", "auto_rollback": True},
    "db_rollback": {"method": "db_rollback", "steps": ["Run down migration", "Restore previous schema", "Verify data integrity"], "validation": ["Data integrity verified", "Schema matches"], "estimated_duration": "15m", "auto_rollback": False},
    "feature_flag": {"method": "feature_flag", "steps": ["Disable feature flag", "Clear cached state", "Restore previous behavior"], "validation": ["Feature disabled"], "estimated_duration": "1m", "auto_rollback": True},
    "full_rollback": {"method": "full_rollback", "steps": ["Restore previous deployment", "Rerun migrations", "Validate health"], "validation": ["Deployment restored", "Services healthy"], "estimated_duration": "20m", "auto_rollback": True},
}


class ReleaseEngine:
    def __init__(self):
        pass

    def _get_db(self):
        return SessionLocal()

    def _to_dict(self, rc: ReleaseCandidateModel) -> Dict:
        return {"id": rc.id, "version": rc.version, "release_type": rc.release_type,
                "state": rc.state, "checks": rc.checks or {},
                "rollback_strategy": rc.rollback_strategy, "approved_by": rc.approved_by,
                "deployed_at": str(rc.deployed_at) if rc.deployed_at else None,
                "rollback_at": str(rc.rollback_at) if rc.rollback_at else None,
                "rollback_reason": rc.rollback_reason,
                "created_at": str(rc.created_at) if rc.created_at else None,
                "updated_at": str(rc.updated_at) if rc.updated_at else None}

    def create_candidate(self, version: str, release_type: str = "patch") -> Dict:
        db = self._get_db()
        try:
            rc = ReleaseCandidateModel(version=version, release_type=release_type, state="draft")
            rc.checks = {"tests_passed": False, "review_passed": False, "quality_gate_passed": False, "approval_granted": False}
            rc.rollback_strategy = ROLLBACK_STRATEGIES["full_rollback"]
            db.add(rc)
            db.commit()
            db.refresh(rc)
            return self._to_dict(rc)
        finally:
            db.close()

    def _get_rc(self, candidate_id: str, db) -> Optional[ReleaseCandidateModel]:
        try:
            uid = int(candidate_id.split("-")[-1]) if "-" in candidate_id else int(candidate_id)
        except ValueError:
            uid = candidate_id
        return db.query(ReleaseCandidateModel).filter(ReleaseCandidateModel.id == uid if isinstance(uid, int) else ReleaseCandidateModel.id == uid).first()

    def approve_candidate(self, candidate_id: str, approved_by: str = "manager") -> Optional[Dict]:
        db = self._get_db()
        try:
            rc = self._get_rc(candidate_id, db)
            if not rc:
                return None
            rc.state = ReleaseState.APPROVED.value
            rc.approved_by = approved_by
            db.commit()
            db.refresh(rc)
            return self._to_dict(rc)
        finally:
            db.close()

    def deploy(self, candidate_id: str) -> Optional[Dict]:
        db = self._get_db()
        try:
            rc = self._get_rc(candidate_id, db)
            if not rc or rc.state != ReleaseState.APPROVED.value:
                return None
            rc.state = ReleaseState.DEPLOYED.value
            rc.deployed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(rc)
            return self._to_dict(rc)
        finally:
            db.close()

    def rollback(self, candidate_id: str, reason: str) -> Optional[Dict]:
        db = self._get_db()
        try:
            rc = self._get_rc(candidate_id, db)
            if not rc:
                return None
            rc.state = ReleaseState.ROLLED_BACK.value
            rc.rollback_at = datetime.now(timezone.utc)
            rc.rollback_reason = reason
            db.commit()
            db.refresh(rc)
            return self._to_dict(rc)
        finally:
            db.close()

    def set_check(self, candidate_id: str, check_name: str, passed: bool) -> Optional[Dict]:
        db = self._get_db()
        try:
            rc = self._get_rc(candidate_id, db)
            if not rc:
                return None
            checks = rc.checks or {}
            if check_name in checks:
                checks[check_name] = passed
            else:
                for key in checks:
                    if key.replace("_", "").startswith(check_name.replace("_", "")):
                        checks[key] = passed
                        break
            rc.checks = checks
            db.commit()
            return {"checks": checks}
        finally:
            db.close()

    def get_strategies(self) -> Dict[str, Dict]:
        return ROLLBACK_STRATEGIES

    def select_strategy(self, candidate_id: str, strategy_name: str) -> Optional[Dict]:
        db = self._get_db()
        try:
            rc = self._get_rc(candidate_id, db)
            if not rc or strategy_name not in ROLLBACK_STRATEGIES:
                return None
            rc.rollback_strategy = ROLLBACK_STRATEGIES[strategy_name]
            db.commit()
            return self._to_dict(rc)
        finally:
            db.close()

    def get_candidate(self, candidate_id: str) -> Optional[Dict]:
        db = self._get_db()
        try:
            rc = self._get_rc(candidate_id, db)
            return self._to_dict(rc) if rc else None
        finally:
            db.close()


release_engine = ReleaseEngine()
