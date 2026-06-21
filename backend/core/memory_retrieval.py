from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import math


class AgentType(str, Enum):
    MANAGER = "manager"
    ARCHITECT = "architect"
    PLANNER = "planner"
    CODER = "coder"
    TESTER = "tester"
    DEBUGGER = "debugger"
    REVIEWER = "reviewer"
    MEMORY = "memory"


class RetrievalMode(str, Enum):
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REVIEW = "review"
    LEARNING = "learning"
    RESEARCH = "research"
    OPTIMIZATION = "optimization"


AGENT_RETRIEVAL_PROFILES: Dict[str, Dict[str, float]] = {
    "manager": {"project_status": 1.0, "risks": 0.9, "milestones": 0.8, "dependencies": 0.7,
                 "decisions": 0.9, "lessons": 0.8, "improvements": 0.7},
    "architect": {"architecture_decisions": 1.0, "tradeoffs": 0.9, "constraints": 0.8,
                   "technology_comparisons": 0.7, "scalability": 0.7, "architecture_lessons": 0.8},
    "planner": {"requirements": 1.0, "research": 0.8, "dependencies": 0.8,
                 "risks": 0.9, "lessons": 0.7, "decision_history": 0.7, "roadmaps": 0.6},
    "coder": {"implementation_patterns": 1.0, "coding_standards": 0.8, "past_solutions": 0.9,
               "project_structure": 0.7, "technical_debt": 0.6, "refactoring_history": 0.5},
    "tester": {"test_results": 1.0, "coverage": 0.8, "regression_history": 0.9,
                "validation_rules": 0.7, "quality_findings": 0.8, "testing_lessons": 0.7},
    "debugger": {"bug_records": 1.0, "root_causes": 0.9, "lessons": 0.8,
                  "architecture_decisions": 0.6, "technical_debt": 0.6, "related_implementations": 0.7},
    "reviewer": {"architecture_reviews": 1.0, "security_findings": 0.9, "maintainability": 0.8,
                  "complexity": 0.7, "technical_debt": 0.7, "quality_lessons": 0.8},
    "memory": {"knowledge_relationships": 1.0, "memory_quality": 0.8, "duplicates": 0.7,
                "retention": 0.6, "compression": 0.6, "knowledge_artifacts": 0.8},
}

MODE_RETRIEVAL_PROFILES: Dict[str, List[str]] = {
    "planning": ["requirements", "research", "risks", "dependencies", "milestones", "lessons"],
    "architecture": ["architecture_decisions", "tradeoffs", "technology_comparisons", "constraints", "scalability"],
    "implementation": ["implementation_patterns", "past_solutions", "coding_standards", "project_structure"],
    "testing": ["test_results", "coverage", "regression_history", "validation_rules"],
    "debugging": ["bug_records", "root_causes", "lessons", "architecture_decisions", "technical_debt", "related_implementations"],
    "review": ["architecture_reviews", "security_findings", "quality_findings", "complexity", "technical_debt"],
    "learning": ["lessons", "improvements", "patterns", "knowledge_artifacts"],
    "research": ["technology_comparisons", "research", "architecture_decisions", "lessons"],
    "optimization": ["technical_debt", "scalability", "performance", "refactoring_history"],
}

DEFAULT_WEIGHTS = {
    "context_match": 0.25,
    "importance": 0.18,
    "confidence": 0.15,
    "outcome_quality": 0.15,
    "frequency": 0.10,
    "relationship_strength": 0.10,
    "recency": 0.07,
}

TOP_N_DEFAULTS = {"simple": 5, "moderate": 10, "complex": 15, "large": 20}


@dataclass
class MemoryRecord:
    id: str
    content: str
    tags: List[str] = field(default_factory=list)
    importance: float = 0.5
    confidence: float = 0.7
    outcome_quality: float = 0.5
    frequency: int = 1
    relationships: List[str] = field(default_factory=list)
    created_at: str = ""
    agent: str = ""


@dataclass
class ScoredMemory:
    record: MemoryRecord
    score: float
    factors: Dict[str, float]


class MemoryRetriever:
    def __init__(self):
        self.memories: List[MemoryRecord] = []
        self._counter = 0

    def add_memory(self, content: str, tags: Optional[List[str]] = None,
                   importance: float = 0.5, confidence: float = 0.7,
                   outcome_quality: float = 0.5, relationships: Optional[List[str]] = None,
                   agent: str = "") -> Dict:
        self._counter += 1
        mem = MemoryRecord(
            id=f"MEM-{self._counter:05d}",
            content=content,
            tags=tags or [],
            importance=importance,
            confidence=confidence,
            outcome_quality=outcome_quality,
            relationships=relationships or [],
            agent=agent,
        )
        self.memories.append(mem)
        return {"id": mem.id, "content": mem.content[:80], "tags": mem.tags}

    def retrieve(self, query: str, agent: str = "", mode: str = "",
                 context_tags: Optional[List[str]] = None,
                 task_complexity: str = "moderate",
                 weights: Optional[Dict[str, float]] = None,
                 top_n: Optional[int] = None) -> Dict:
        w = weights or DEFAULT_WEIGHTS
        limit = top_n or TOP_N_DEFAULTS.get(task_complexity, 10)

        if not self.memories:
            return {"memories": [], "summary": "No memories available", "confidence": 0.0}

        scored = []
        for mem in self.memories:
            factors = {}
            context_score = self._score_context(mem, query, context_tags or [], agent, mode)
            factors["context_match"] = context_score

            importance = mem.importance
            factors["importance"] = importance

            confidence = mem.confidence
            factors["confidence"] = confidence

            outcome = mem.outcome_quality
            factors["outcome_quality"] = outcome

            freq = min(mem.frequency / 10.0, 1.0)
            factors["frequency"] = freq

            rel = min(len(mem.relationships) / 5.0, 1.0)
            factors["relationship_strength"] = rel

            recency = self._score_recency(mem)
            factors["recency"] = recency

            score = sum(factors[k] * w.get(k, 0) for k in factors)
            scored.append(ScoredMemory(record=mem, score=score, factors=factors))

        scored.sort(key=lambda x: x.score, reverse=True)
        top = scored[:limit]

        contradictions = self._detect_contradictions(top)
        knowledge_graph = self._build_graph(top)
        summary = self._summarize(top, contradictions)

        return {
            "query": query,
            "agent": agent,
            "mode": mode,
            "memories": [{"id": s.record.id, "content": s.record.content[:120],
                          "score": round(s.score, 3), "factors": {k: round(v, 3) for k, v in s.factors.items()},
                          "tags": s.record.tags, "agent": s.record.agent}
                         for s in top],
            "summary": summary,
            "contradictions": contradictions,
            "knowledge_graph": knowledge_graph,
            "confidence": round(sum(s.score for s in top) / len(top), 3) if top else 0.0,
        }

    def _score_context(self, mem: MemoryRecord, query: str, context_tags: List[str],
                       agent: str, mode: str) -> float:
        score = 0.0
        q = query.lower()
        content_lower = mem.content.lower()
        query_words = set(q.split())

        for word in query_words:
            if word in content_lower:
                score += 0.3
        if q and q in content_lower:
            score += 0.4

        for tag in mem.tags:
            if q in tag.lower():
                score += 0.2
                break

        if context_tags:
            match = sum(1 for t in context_tags if t in mem.tags)
            score += min(match * 0.2, 0.6)

        if agent:
            profile = AGENT_RETRIEVAL_PROFILES.get(agent, {})
            for tag in mem.tags:
                if tag in profile:
                    score += profile[tag] * 0.3

        if mode:
            mode_tags = MODE_RETRIEVAL_PROFILES.get(mode, [])
            for tag in mem.tags:
                if tag in mode_tags:
                    score += 0.2

        return min(score, 1.0)

    def _score_recency(self, mem: MemoryRecord) -> float:
        from datetime import datetime
        if not mem.created_at:
            return 0.5
        try:
            created = datetime.fromisoformat(mem.created_at)
            age = (datetime.utcnow() - created).total_seconds()
            days = age / 86400
            return max(0.0, 1.0 - days * 0.01)
        except Exception:
            return 0.5

    def _detect_contradictions(self, scored: List[ScoredMemory]) -> List[Dict]:
        contradictions = []
        opposites = {"use": "avoid", "do": "dont", "enable": "disable", "allow": "block",
                      "include": "exclude", "start": "stop", "add": "remove", "create": "delete",
                      "increase": "decrease", "upgrade": "downgrade", "always": "never",
                      "recommend": "discourage", "positive": "negative"}

        for i in range(len(scored)):
            for j in range(i + 1, len(scored)):
                a, b = scored[i], scored[j]
                a_tags, b_tags = set(a.record.tags), set(b.record.tags)
                tag_overlap = a_tags & b_tags
                if len(tag_overlap) >= 2 and a.score > 0.3 and b.score > 0.3:
                    a_lower = a.record.content.lower()
                    b_lower = b.record.content.lower()
                    a_words = set(a_lower.split())
                    b_words = set(b_lower.split())
                    conflict_pairs = []
                    for pos, neg in opposites.items():
                        if (pos in a_words and neg in b_words) or (neg in a_words and pos in b_words):
                            conflict_pairs.append(f"{pos}/{neg}")
                    if conflict_pairs or (len(a_tags & b_tags) >= 2 and a_lower[:20] != b_lower[:20]):
                        contradictions.append({
                            "memory_a": a.record.id,
                            "memory_b": b.record.id,
                            "common_tags": list(tag_overlap),
                            "conflicts": conflict_pairs if conflict_pairs else ["different direction"],
                        })
        return contradictions

    def _build_graph(self, scored: List[ScoredMemory]) -> Dict[str, List[str]]:
        graph: Dict[str, List[str]] = {}
        for s in scored:
            mem_id = s.record.id
            if mem_id not in graph:
                graph[mem_id] = []
            for tag in s.record.tags:
                if tag not in graph:
                    graph[tag] = []
                graph[tag].append(mem_id)
                graph[mem_id].append(tag)
            for rel in s.record.relationships:
                graph[mem_id].append(rel)
        return graph

    def _summarize(self, scored: List[ScoredMemory], contradictions: List[Dict]) -> str:
        if not scored:
            return "No relevant memories found."
        top_tags = {}
        for s in scored:
            for tag in s.record.tags:
                top_tags[tag] = top_tags.get(tag, 0) + 1
        top_tags = sorted(top_tags.items(), key=lambda x: -x[1])[:5]
        tag_summary = ", ".join(f"{t} ({c}x)" for t, c in top_tags)
        contradiction_note = f" {len(contradictions)} contradiction(s) detected." if contradictions else ""
        return f"Top {len(scored)} memories. Key topics: {tag_summary}.{contradiction_note}"

    def expand_relationships(self, query: str, agent: str = "", mode: str = "",
                             context_tags: Optional[List[str]] = None,
                             task_complexity: str = "moderate") -> Dict:
        base = self.retrieve(query, agent, mode, context_tags, task_complexity)

        related_ids = set()
        for m in base["memories"]:
            mem_id = m["id"]
            for mem in self.memories:
                if mem.id == mem_id:
                    related_ids.update(mem.relationships)
                    break

        related_memories = []
        for mem in self.memories:
            if mem.id in related_ids and mem.id not in {m["id"] for m in base["memories"]}:
                related_memories.append({
                    "id": mem.id, "content": mem.content[:120],
                    "tags": mem.tags, "relationship_type": "expanded",
                })

        base["expanded_memories"] = related_memories[:5]
        base["total_expanded"] = len(related_memories)
        return base

    def get_profile(self, agent: str) -> Dict:
        return {"agent": agent, "profile": AGENT_RETRIEVAL_PROFILES.get(agent, {})}
