from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class TaskType(str, Enum):
    LEARNING = "learning"
    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    ARCHITECTURE = "architecture"
    RESEARCH = "research"
    REFACTOR = "refactor"
    DEPLOYMENT = "deployment"
    RELEASE = "release"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    PROJECT_PLANNING = "project_planning"
    SYSTEM_DESIGN = "system_design"
    LARGE_PROJECT = "large_project"
    REVIEW = "review"
    TESTING = "testing"
    DEBUGGING = "debugging"
    GENERAL = "general"


TASK_KEYWORDS: Dict[TaskType, List[str]] = {
    TaskType.LEARNING: ["learn", "teach", "explain", "understand", "concept", "tutorial"],
    TaskType.BUG_FIX: ["bug", "error", "fail", "broken", "crash", "wrong", "incorrect", "fix"],
    TaskType.FEATURE: ["feature", "add", "new", "create", "implement", "build", "enhance"],
    TaskType.ARCHITECTURE: ["architect", "design", "structure", "component", "module", "system design"],
    TaskType.RESEARCH: ["research", "investigate", "explore", "find", "search", "compare", "alternatives"],
    TaskType.REFACTOR: ["refactor", "clean", "improve", "restructure", "modernize", "rewrite"],
    TaskType.DEPLOYMENT: ["deploy", "release", "ci/cd", "pipeline", "production"],
    TaskType.RELEASE: ["release", "version", "tag", "changelog", "ship"],
    TaskType.PERFORMANCE: ["performance", "slow", "speed", "latency", "optimize", "benchmark", "throughput"],
    TaskType.DOCUMENTATION: ["document", "readme", "doc", "comment", "api doc", "guide"],
    TaskType.PROJECT_PLANNING: ["plan", "roadmap", "milestone", "sprint", "epic", "story"],
    TaskType.SYSTEM_DESIGN: ["system design", "high-level", "architecture design", "distributed"],
    TaskType.LARGE_PROJECT: ["large", "multi-stage", "complex", "initiative", "platform"],
    TaskType.REVIEW: ["review", "audit", "inspect", "check quality"],
    TaskType.TESTING: ["test", "coverage", "validate", "qa", "quality assurance"],
    TaskType.DEBUGGING: ["debug", "trace", "root cause", "diagnose", "reproduce"],
}


COMPLEXITY_KEYWORDS: Dict[str, List[str]] = {
    "simple": ["quick", "simple", "easy", "trivial", "minor", "small"],
    "moderate": ["moderate", "medium", "normal", "standard"],
    "complex": ["complex", "difficult", "challenging", "hard", "significant"],
    "critical": ["critical", "urgent", "emergency", "large", "major", "massive"],
}


@dataclass
class ClassificationResult:
    task_type: TaskType
    confidence: float
    complexity: str
    complexity_score: int
    scope: str
    risk: str
    keywords: List[str] = field(default_factory=list)
    needs_architecture: bool = False
    needs_research: bool = False
    needs_security_review: bool = False
    needs_approval: bool = False
    estimated_effort: str = "medium"


class TaskClassifier:
    def classify(self, description: str, title: Optional[str] = None) -> ClassificationResult:
        text = f"{title or ''} {description}".lower()
        scores: Dict[TaskType, int] = {}
        matched_keywords: List[str] = []

        for task_type, keywords in TASK_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if kw in text:
                    score += 1
                    matched_keywords.append(kw)
            if score > 0:
                scores[task_type] = score

        if not scores:
            return ClassificationResult(
                task_type=TaskType.GENERAL,
                confidence=0.3,
                complexity="simple",
                complexity_score=1,
                scope="small",
                risk="low",
                estimated_effort="small",
            )

        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]
        total_score = sum(scores.values())
        confidence = min(0.3 + (max_score / max(total_score, 1)) * 0.5, 0.95)

        word_count = len(description.split())
        complexity_score = self._score_complexity(text, word_count)

        risk = "low"
        if complexity_score >= 10:
            risk = "high"
        elif complexity_score >= 6:
            risk = "medium"

        scope = "small" if word_count < 30 else "medium" if word_count < 100 else "large"

        return ClassificationResult(
            task_type=best_type,
            confidence=round(confidence, 2),
            complexity=self._complexity_label(complexity_score),
            complexity_score=complexity_score,
            scope=scope,
            risk=risk,
            keywords=matched_keywords[:10],
            needs_architecture=best_type in (TaskType.ARCHITECTURE, TaskType.SYSTEM_DESIGN, TaskType.LARGE_PROJECT) or complexity_score >= 8,
            needs_research=best_type in (TaskType.RESEARCH, TaskType.LEARNING) or complexity_score >= 6,
            needs_security_review=best_type in (TaskType.DEPLOYMENT, TaskType.RELEASE) or risk == "high",
            needs_approval=risk == "high" or best_type in (TaskType.DEPLOYMENT, TaskType.RELEASE, TaskType.LARGE_PROJECT),
            estimated_effort=self._estimate_effort(complexity_score, best_type),
        )

    def _score_complexity(self, text: str, word_count: int) -> int:
        score = 0
        for level, keywords in COMPLEXITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    level_scores = {"simple": 1, "moderate": 3, "complex": 6, "critical": 10}
                    score += level_scores.get(level, 0)
        if word_count > 200:
            score += 4
        elif word_count > 100:
            score += 2
        elif word_count > 50:
            score += 1
        return min(score, 20)

    def _complexity_label(self, score: int) -> str:
        if score <= 2:
            return "simple"
        if score <= 6:
            return "moderate"
        if score <= 12:
            return "complex"
        return "critical"

    def _estimate_effort(self, score: int, task_type: TaskType) -> str:
        if task_type == TaskType.LARGE_PROJECT:
            return "large"
        if score <= 2:
            return "small"
        if score <= 6:
            return "medium"
        return "large"


task_classifier = TaskClassifier()
