from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ArtifactStatus(str, Enum):
    OBSERVATION = "observation"
    PATTERN = "pattern"
    KNOWLEDGE_ARTIFACT = "knowledge_artifact"
    CANDIDATE_RULE = "candidate_rule"
    APPROVED_RULE = "approved_rule"
    SUPERSEDED = "superseded"


@dataclass
class KnowledgeArtifact:
    id: str
    title: str
    status: ArtifactStatus
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    source_count: int = 1
    conclusion: str = ""
    reusable: bool = False
    tags: List[str] = field(default_factory=list)
    source_ids: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass
class CandidateRule:
    id: str
    title: str
    evidence: str
    confidence: float
    recommendation: str
    review_status: str = "pending"
    created_at: str = ""
    reviewed_at: Optional[str] = None


PROMOTION_THRESHOLDS = {
    "pattern": 0.70,
    "knowledge_artifact": 0.85,
    "candidate_rule": 0.95,
}


class KnowledgeEngine:
    def __init__(self):
        self.artifacts: List[KnowledgeArtifact] = []
        self.candidate_rules: List[CandidateRule] = []
        self.approved_rules: List[CandidateRule] = []

    def _next_id(self, prefix: str) -> str:
        return f"{prefix}-{len(self.artifacts) + len(self.candidate_rules) + 1:03d}"

    def promote_from_patterns(self, patterns: List[Dict]) -> List[KnowledgeArtifact]:
        promoted = []
        for p in patterns:
            category = p.get("category", "unknown")
            entry_count = p.get("entry_count", 1)
            common_topics = p.get("pattern", {}).get("common_topics", [])
            if entry_count < 3 or not common_topics:
                continue
            confidence = min(entry_count * 0.05 + 0.5, 0.95)
            if confidence >= PROMOTION_THRESHOLDS["knowledge_artifact"]:
                artifact = KnowledgeArtifact(
                    id=self._next_id("KA"),
                    title=f"Pattern: {category} - {', '.join(common_topics[:5])}",
                    status=ArtifactStatus.KNOWLEDGE_ARTIFACT,
                    evidence=[f"Derived from {entry_count} entries in {category}"],
                    confidence=round(confidence, 2),
                    source_count=entry_count,
                    conclusion=f"Repeated {category} patterns found: {', '.join(common_topics[:5])}",
                    reusable=True,
                    tags=common_topics[:5],
                    created_at=datetime.utcnow().isoformat(),
                    updated_at=datetime.utcnow().isoformat(),
                )
                self.artifacts.append(artifact)

                if confidence >= PROMOTION_THRESHOLDS["candidate_rule"]:
                    rule = CandidateRule(
                        id=self._next_id("CR"),
                        title=f"Rule: {category}",
                        evidence=f"Pattern repeated across {entry_count} entries with {confidence:.0%} confidence",
                        confidence=round(confidence, 2),
                        recommendation=f"Consider standardizing {category} approach",
                        created_at=datetime.utcnow().isoformat(),
                    )
                    self.candidate_rules.append(rule)
                    artifact.status = ArtifactStatus.CANDIDATE_RULE
                promoted.append(artifact)
        return promoted

    def record_observation(self, title: str, content: str, tags: Optional[List[str]] = None) -> KnowledgeArtifact:
        obs = KnowledgeArtifact(
            id=self._next_id("OBS"),
            title=title,
            status=ArtifactStatus.OBSERVATION,
            evidence=[content[:500]],
            confidence=0.3,
            source_count=1,
            conclusion=content[:300],
            tags=tags or [],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )
        self.artifacts.append(obs)
        return obs

    def review_rule(self, rule_id: str, approve: bool) -> Optional[Dict]:
        for rule in self.candidate_rules:
            if rule.id == rule_id:
                if approve:
                    rule.review_status = "approved"
                    rule.reviewed_at = datetime.utcnow().isoformat()
                    self.approved_rules.append(rule)
                else:
                    rule.review_status = "rejected"
                    rule.reviewed_at = datetime.utcnow().isoformat()
                return {"rule_id": rule.id, "status": rule.review_status,
                        "approved": approve, "reviewed_at": rule.reviewed_at}
        return None

    def get_artifacts(self, status: Optional[str] = None) -> List[Dict]:
        results = self.artifacts
        if status:
            results = [a for a in results if a.status.value == status]
        return [a.__dict__ for a in results]

    def get_candidate_rules(self, status: str = "pending") -> List[Dict]:
        return [r.__dict__ for r in self.candidate_rules if r.review_status == status]

    def get_approved_rules(self) -> List[Dict]:
        return [r.__dict__ for r in self.approved_rules]


knowledge_engine = KnowledgeEngine()
