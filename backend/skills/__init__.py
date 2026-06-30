from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod


@dataclass
class SkillResult:
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseSkill(ABC):
    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.version = version

    @abstractmethod
    async def execute(self, context: Dict[str, Any], **kwargs) -> SkillResult:
        pass


_SKILL_REGISTRY: Dict[str, BaseSkill] = {}
_SKILL_LOG: List[Dict] = []


def register(skill: BaseSkill):
    _SKILL_REGISTRY[skill.name] = skill


def get(name: str) -> Optional[BaseSkill]:
    return _SKILL_REGISTRY.get(name)


def list_skills() -> List[Dict]:
    return [{"name": s.name, "description": s.description, "version": s.version}
            for s in _SKILL_REGISTRY.values()]


def log_use(entry: Dict):
    entry["timestamp"] = datetime.utcnow().isoformat()
    _SKILL_LOG.append(entry)


def get_log(limit: int = 50) -> List[Dict]:
    return _SKILL_LOG[-limit:]
