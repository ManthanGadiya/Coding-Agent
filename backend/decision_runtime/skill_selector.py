from typing import Any, Dict, List, Optional, Set

from backend.decision_runtime.registries import skill_registry, SkillDef
from backend.decision_runtime.task_classifier import TaskType, ClassificationResult


SKILL_TASK_MAP: Dict[TaskType, List[str]] = {
    TaskType.LARGE_PROJECT: ["autoplan"],
    TaskType.BUG_FIX: ["investigate"],
    TaskType.DEBUGGING: ["investigate"],
    TaskType.REVIEW: ["review"],
    TaskType.PERFORMANCE: ["benchmark"],
    TaskType.RELEASE: ["health", "benchmark"],
    TaskType.DEPLOYMENT: ["health"],
    TaskType.FEATURE: ["design-review"],
    TaskType.ARCHITECTURE: ["plan-eng-review"],
    TaskType.SYSTEM_DESIGN: ["plan-eng-review"],
    TaskType.PROJECT_PLANNING: ["plan-ceo-review", "plan-eng-review"],
    TaskType.RESEARCH: ["temp_websearch_skill"],
    TaskType.LEARNING: ["temp_websearch_skill"],
    TaskType.TESTING: ["agent-browser"],
}


class SkillSelector:
    def select(self, classification: ClassificationResult,
                context: Optional[Dict] = None) -> List[SkillDef]:
        selected_skills: List[SkillDef] = []
        seen: Set[str] = set()

        task_skills = SKILL_TASK_MAP.get(classification.task_type, [])
        for skill_name in task_skills:
            if skill_name not in seen:
                skill = skill_registry.get(skill_name)
                if skill and skill.enabled:
                    selected_skills.append(skill)
                    seen.add(skill_name)

        if classification.needs_research:
            skill = skill_registry.get("temp_websearch_skill")
            if skill and skill.enabled and skill.name not in seen:
                selected_skills.append(skill)
                seen.add(skill.name)

        if classification.complexity in ("complex", "critical") or classification.needs_architecture:
            for name in ["plan-eng-review", "autoplan"]:
                if name not in seen:
                    skill = skill_registry.get(name)
                    if skill and skill.enabled:
                        selected_skills.append(skill)
                        seen.add(name)

        return selected_skills

    def select_by_condition(self, condition: str) -> List[SkillDef]:
        return skill_registry.find_by_condition(condition)


skill_selector = SkillSelector()
