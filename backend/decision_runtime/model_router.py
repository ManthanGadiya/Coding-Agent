from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from backend.decision_runtime.registries import model_registry, ModelDef
from backend.decision_runtime.task_classifier import TaskType, ClassificationResult


MODEL_TASK_MAP: Dict[TaskType, str] = {
    TaskType.LEARNING: "cloud-balanced",
    TaskType.BUG_FIX: "local-medium",
    TaskType.FEATURE: "local-large",
    TaskType.ARCHITECTURE: "cloud-reasoning",
    TaskType.RESEARCH: "local-medium",
    TaskType.REFACTOR: "local-large",
    TaskType.DEPLOYMENT: "local-medium",
    TaskType.RELEASE: "local-large",
    TaskType.PERFORMANCE: "local-medium",
    TaskType.DOCUMENTATION: "local-small",
    TaskType.PROJECT_PLANNING: "cloud-balanced",
    TaskType.SYSTEM_DESIGN: "cloud-reasoning",
    TaskType.LARGE_PROJECT: "cloud-reasoning",
    TaskType.REVIEW: "cloud-balanced",
    TaskType.TESTING: "local-small",
    TaskType.DEBUGGING: "local-medium",
    TaskType.GENERAL: "local-small",
}


MODEL_COMPLEXITY_MAP: Dict[str, str] = {
    "simple": "local-small",
    "moderate": "local-medium",
    "complex": "local-large",
    "critical": "cloud-reasoning",
}


@dataclass
class ModelSelection:
    primary: ModelDef
    fallback: Optional[ModelDef] = None
    reasoning: str = ""
    estimated_cost: float = 0.0
    estimated_latency_ms: int = 0


class RuntimeModelRouter:
    def select(self, classification: ClassificationResult,
                available_models: Optional[List[str]] = None,
                prefer_local: bool = True,
                context: Optional[Dict] = None) -> ModelSelection:
        preferred_name = MODEL_TASK_MAP.get(classification.task_type, "local-small")
        preferred = model_registry.get(preferred_name)

        if not preferred or not preferred.enabled:
            fallback_name = MODEL_COMPLEXITY_MAP.get(classification.complexity, "local-small")
            preferred = model_registry.get(fallback_name)

        if not preferred or not preferred.enabled:
            preferred = self._first_available(available_models)

        if not preferred:
            preferred = model_registry.get("local-small")

        if prefer_local and preferred and preferred.provider != "ollama":
            local = self._find_local_by_capability(preferred.capabilities)
            if local:
                preferred = local

        fallback = self._find_fallback(preferred, available_models)

        return ModelSelection(
            primary=preferred,
            fallback=fallback,
            reasoning=f"Task '{classification.task_type.value}' → {preferred.name} ({preferred.provider})",
            estimated_cost=preferred.cost_per_token if preferred else 0,
            estimated_latency_ms=preferred.latency_ms if preferred else 0,
        )

    def select_for_complexity(self, complexity: str) -> Optional[ModelDef]:
        name = MODEL_COMPLEXITY_MAP.get(complexity, "local-small")
        return model_registry.get(name)

    def select_by_capability(self, capability: str) -> List[ModelDef]:
        return [m for m in model_registry.list() if capability in m.capabilities]

    def _first_available(self, names: Optional[List[str]]) -> Optional[ModelDef]:
        if not names:
            return None
        for name in names:
            m = model_registry.get(name)
            if m and m.enabled:
                return m
        return None

    def _find_local_by_capability(self, capabilities: List[str]) -> Optional[ModelDef]:
        for model in model_registry.list():
            if model.enabled and model.provider == "ollama":
                if any(c in model.capabilities for c in capabilities):
                    return model
        return None

    def _find_fallback(self, preferred: Optional[ModelDef],
                        available: Optional[List[str]]) -> Optional[ModelDef]:
        if not preferred:
            return None
        for model in model_registry.list():
            if model.enabled and model.name != preferred.name:
                if model.provider != preferred.provider:
                    for cap in preferred.capabilities:
                        if cap in model.capabilities:
                            return model
        return None


runtime_model_router = RuntimeModelRouter()
