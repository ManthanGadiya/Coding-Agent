from typing import Dict, List, Optional
from enum import Enum


class EnvironmentMode(str, Enum):
    TEACHING = "teaching"
    BUILD = "build"
    FULL = "full"
    AUTONOMOUS = "autonomous"


MODE_PRIORITIES: Dict[EnvironmentMode, List[str]] = {
    EnvironmentMode.TEACHING: [
        "learning", "maintainability", "correctness",
        "reliability", "performance", "speed",
    ],
    EnvironmentMode.BUILD: [
        "maintainability", "correctness", "reliability",
        "learning", "performance", "speed",
    ],
    EnvironmentMode.FULL: [
        "correctness", "safety", "reliability", "maintainability",
        "security", "performance", "learning", "speed",
    ],
    EnvironmentMode.AUTONOMOUS: [
        "correctness", "reliability", "maintainability",
        "security", "performance", "learning", "speed",
    ],
}


class ModeController:
    def __init__(self, mode: EnvironmentMode = EnvironmentMode.BUILD):
        self._mode = mode

    @property
    def mode(self) -> EnvironmentMode:
        return self._mode

    def set_mode(self, mode: EnvironmentMode):
        self._mode = mode

    def priorities(self, mode: Optional[EnvironmentMode] = None) -> List[str]:
        m = mode if mode is not None else self._mode
        return MODE_PRIORITIES.get(m, MODE_PRIORITIES[EnvironmentMode.BUILD])

    def rank(self, objective: str) -> int:
        prio = self.priorities()
        try:
            return prio.index(objective)
        except ValueError:
            return len(prio)

    def is_higher_priority_than(self, a: str, b: str) -> bool:
        return self.rank(a) < self.rank(b)

    def weight(self, objective: str) -> float:
        prio = self.priorities()
        total = len(prio)
        try:
            idx = prio.index(objective)
        except ValueError:
            return 0.0
        return round(1.0 - (idx / total), 3)


mode_controller = ModeController()
