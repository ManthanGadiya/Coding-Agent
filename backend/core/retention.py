from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class RetentionLevel(str, Enum):
    TEMPORARY = "temporary"
    STANDARD = "standard"
    LONG_TERM = "long_term"
    PERMANENT = "permanent"


RETENTION_DAYS = {
    RetentionLevel.TEMPORARY: 30,
    RetentionLevel.STANDARD: 180,
    RetentionLevel.LONG_TERM: 365,
    RetentionLevel.PERMANENT: None,
}

STALE_THRESHOLD_DAYS = 90
LOW_CONFIDENCE_THRESHOLD = 0.3
MIN_ENTRIES_FOR_ARCHIVAL = 3


@dataclass
class RetentionScore:
    entry_id: str
    score: float
    importance: float
    confidence: float
    frequency: float
    outcome_quality: float
    retention_level: RetentionLevel
    is_stale: bool
    should_archive: bool


class RetentionEngine:
    def score_entry(self, entry: Dict) -> RetentionScore:
        importance = min(entry.get("usage_count", 0) * 0.1, 1.0)
        confidence_map = {"high": 1.0, "medium": 0.6, "low": 0.3}
        confidence = confidence_map.get(entry.get("confidence", "medium"), 0.5)
        frequency = min(entry.get("usage_count", 0) / 20, 1.0)

        meta = entry.get("extra_metadata") or {}
        version_count = len(meta.get("versions", []))
        outcome_quality = min(version_count * 0.1 + confidence * 0.5, 1.0)

        score = importance * 0.3 + confidence * 0.25 + frequency * 0.2 + outcome_quality * 0.25

        level = RetentionLevel.PERMANENT
        if score < 0.3:
            level = RetentionLevel.TEMPORARY
        elif score < 0.5:
            level = RetentionLevel.STANDARD
        elif score < 0.8:
            level = RetentionLevel.LONG_TERM

        last_accessed = entry.get("last_accessed")
        is_stale = False
        if last_accessed:
            try:
                last = datetime.fromisoformat(last_accessed) if isinstance(last_accessed, str) else last_accessed
                is_stale = (datetime.utcnow() - last).days > STALE_THRESHOLD_DAYS and score < 0.5
            except (ValueError, TypeError):
                is_stale = score < 0.3
        else:
            is_stale = score < 0.3

        should_archive = is_stale and score < LOW_CONFIDENCE_THRESHOLD

        return RetentionScore(
            entry_id=entry.get("id", ""),
            score=round(score, 3),
            importance=round(importance, 3),
            confidence=round(confidence, 3),
            frequency=round(frequency, 3),
            outcome_quality=round(outcome_quality, 3),
            retention_level=level,
            is_stale=is_stale,
            should_archive=should_archive,
        )

    def get_stale_entries(self, entries: List[Dict]) -> List[RetentionScore]:
        return [self.score_entry(e) for e in entries if self.score_entry(e).is_stale]

    def get_archival_candidates(self, entries: List[Dict]) -> List[Dict]:
        scores = [self.score_entry(e) for e in entries]
        return [{"id": s.entry_id, "score": s.score, "level": s.retention_level.value}
                for s in scores if s.should_archive]

    def health_metrics(self, entries: List[Dict]) -> Dict:
        total = len(entries)
        if total == 0:
            return {"total": 0, "noise_ratio": 0, "knowledge_density": 0, "stale_count": 0}
        scores = [self.score_entry(e) for e in entries]
        stale = [s for s in scores if s.is_stale]
        high_value = [s for s in scores if s.score > 0.7]
        return {
            "total": total,
            "stale_count": len(stale),
            "stale_ratio": round(len(stale) / total, 3),
            "high_value_count": len(high_value),
            "knowledge_density": round(len(high_value) / total, 3),
            "average_score": round(sum(s.score for s in scores) / total, 3),
        }


retention_engine = RetentionEngine()
