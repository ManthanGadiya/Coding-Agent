from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import Counter
import re

from backend.core.database import EngineSession
from backend.models.learning import (
    KnowledgeArtifact as KnowledgeArtifactModel, ArtifactStatus,
    CandidateRule as CandidateRuleModel,
)


PROMOTION_THRESHOLDS = {
    "pattern": 0.70,
    "knowledge_artifact": 0.85,
    "candidate_rule": 0.95,
}


class KnowledgeEngine:
    def __init__(self):
        pass

    def _db(self):
        return EngineSession()

    def promote_from_patterns(self, patterns: List[Dict]) -> List[KnowledgeArtifactModel]:
        db = self._db()
        try:
            promoted = []
            for p in patterns:
                category = p.get("category", "unknown")
                entry_count = p.get("entry_count", 1)
                common_topics = p.get("pattern", {}).get("common_topics", [])
                if entry_count < 3 or not common_topics:
                    continue
                confidence = min(entry_count * 0.05 + 0.5, 0.95)
                if confidence >= PROMOTION_THRESHOLDS["knowledge_artifact"]:
                    artifact = KnowledgeArtifactModel(
                        title=f"Pattern: {category} - {', '.join(common_topics[:5])}",
                        status=ArtifactStatus.KNOWLEDGE_ARTIFACT,
                        evidence=[f"Derived from {entry_count} entries in {category}"],
                        confidence=round(confidence, 2),
                        source_count=entry_count,
                        conclusion=f"Repeated {category} patterns found: {', '.join(common_topics[:5])}",
                        reusable=True,
                        tags=common_topics[:5],
                    )
                    db.add(artifact)
                    db.flush()

                    if confidence >= PROMOTION_THRESHOLDS["candidate_rule"]:
                        rule = CandidateRuleModel(
                            title=f"Rule: {category}",
                            evidence=f"Pattern repeated across {entry_count} entries with {confidence:.0%} confidence",
                            confidence=round(confidence, 2),
                            recommendation=f"Consider standardizing {category} approach",
                        )
                        db.add(rule)
                        artifact.status = ArtifactStatus.CANDIDATE_RULE
                    db.commit()
                    promoted.append(artifact)
            return promoted
        finally:
            db.close()

    def record_observation(self, title: str, content: str, tags: Optional[List[str]] = None) -> KnowledgeArtifactModel:
        db = self._db()
        try:
            obs = KnowledgeArtifactModel(
                title=title, status=ArtifactStatus.OBSERVATION,
                evidence=[content[:500]], confidence=0.3,
                source_count=1, conclusion=content[:300], tags=tags or [],
            )
            db.add(obs)
            db.commit()
            db.refresh(obs)
            return obs
        finally:
            db.close()

    def review_rule(self, rule_id: str, approve: bool) -> Optional[Dict]:
        db = self._db()
        try:
            rule = db.query(CandidateRuleModel).filter(CandidateRuleModel.id == rule_id).first()
            if not rule:
                return None
            if approve:
                rule.review_status = "approved"
                rule.reviewed_at = datetime.utcnow()
            else:
                rule.review_status = "rejected"
                rule.reviewed_at = datetime.utcnow()
            db.commit()
            return {"rule_id": rule.id, "status": rule.review_status, "approved": approve,
                    "reviewed_at": rule.reviewed_at.isoformat() if rule.reviewed_at else ""}
        finally:
            db.close()

    def get_artifacts(self, status: Optional[str] = None) -> List[Dict]:
        db = self._db()
        try:
            q = db.query(KnowledgeArtifactModel)
            if status:
                q = q.filter(KnowledgeArtifactModel.status == ArtifactStatus(status))
            return [{"id": a.id, "title": a.title, "status": a.status.value,
                     "confidence": a.confidence, "source_count": a.source_count,
                     "conclusion": a.conclusion[:200], "tags": a.tags,
                     "created_at": a.created_at.isoformat() if a.created_at else ""} for a in q.all()]
        finally:
            db.close()

    def get_candidate_rules(self, status: str = "pending") -> List[Dict]:
        db = self._db()
        try:
            return [{"id": r.id, "title": r.title, "evidence": r.evidence,
                     "confidence": r.confidence, "recommendation": r.recommendation,
                     "review_status": r.review_status} for r in db.query(CandidateRuleModel).filter(CandidateRuleModel.review_status == status).all()]
        finally:
            db.close()

    def get_approved_rules(self) -> List[Dict]:
        db = self._db()
        try:
            return [{"id": r.id, "title": r.title, "evidence": r.evidence,
                     "confidence": r.confidence, "recommendation": r.recommendation} for r in db.query(CandidateRuleModel).filter(CandidateRuleModel.review_status == "approved").all()]
        finally:
            db.close()


knowledge_engine = KnowledgeEngine()
