from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class DecisionType(str, Enum):
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    ARCHITECTURAL = "architectural"
    STRATEGIC = "strategic"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionEngine:
    def __init__(self):
        self.history: List[Dict] = []

    def decide(
        self,
        objective: str,
        options: List[Dict],
        decision_type: DecisionType = DecisionType.OPERATIONAL,
        constraints: Optional[List[str]] = None,
        evidence: Optional[List[str]] = None,
        risk_assessment: Optional[Dict] = None,
    ) -> Dict:
        steps = [
            ("Understand Objective", self._understand),
            ("Gather Information", self._gather),
            ("Identify Constraints", self._identify_constraints),
            ("Generate Options", self._generate),
            ("Evaluate Options", self._evaluate),
            ("Choose Recommendation", self._choose),
            ("Validate Decision", self._validate),
            ("Execute or Escalate", self._execute),
        ]

        state = {
            "objective": objective,
            "options": options,
            "decision_type": decision_type,
            "constraints": constraints or [],
            "evidence": evidence or [],
            "risk_assessment": risk_assessment or {},
            "context": {},
            "evaluations": [],
            "recommendation": None,
            "confidence": None,
            "risks": [],
            "escalate": False,
        }

        for step_name, step_fn in steps:
            state = step_fn(state)
            state.setdefault("steps_taken", []).append(step_name)

        result = {
            "decision_id": f"DEC-{int(datetime.utcnow().timestamp() * 1000) % 100000:05d}",
            "objective": objective,
            "timestamp": datetime.utcnow().isoformat(),
            "decision_type": decision_type.value,
            "recommendation": state["recommendation"],
            "confidence": state["confidence"],
            "reasoning": state.get("reasoning", ""),
            "risks": state["risks"],
            "alternatives": [o.get("label") for o in options if o.get("label") != state.get("recommendation")],
            "escalate": state["escalate"],
            "steps_taken": state["steps_taken"],
        }
        self.history.append(result)
        return result

    def _understand(self, s: Dict) -> Dict:
        obj = s["objective"]
        if not obj or len(obj) < 5:
            s["escalate"] = True
            s["reasoning"] = "Objective too vague — needs clarification"
        else:
            s["reasoning"] = f"Objective: {obj}"
        return s

    def _gather(self, s: Dict) -> Dict:
        if not s["evidence"]:
            s["confidence_raw"] = 0.3
        else:
            s["confidence_raw"] = min(0.5 + 0.1 * len(s["evidence"]), 0.9)
        return s

    def _identify_constraints(self, s: Dict) -> Dict:
        s["context"]["constraints"] = s["constraints"]
        return s

    def _generate(self, s: Dict) -> Dict:
        if len(s["options"]) < 2:
            s["options"].append({"label": "Alternative approach", "description": "Generated alternative"})
        s["context"]["option_count"] = len(s["options"])
        return s

    def _evaluate(self, s: Dict) -> Dict:
        scores = []
        for opt in s["options"]:
            score = self._score_option(opt, s)
            scores.append(score)
        s["evaluations"] = scores
        s["evaluations_done"] = True
        return s

    def _score_option(self, opt: Dict, s: Dict) -> Dict:
        score = 0
        notes = []

        if opt.get("maintainability", 5) >= 7:
            score += 2
        else:
            score -= 1

        if opt.get("complexity", 5) <= 4:
            score += 1
        else:
            score -= 1

        if opt.get("risk", "medium") in ("low", "very_low"):
            score += 2
        elif opt.get("risk") == "high":
            score -= 2

        cost = opt.get("cost", 5)
        score += max(-2, min(2, (5 - cost) // 2))

        if s.get("evidence"):
            score += min(len(s["evidence"]), 3)

        if opt.get("correctness", 5) >= 7:
            score += 1

        return {"label": opt.get("label", ""), "score": score, "notes": notes}

    def _choose(self, s: Dict) -> Dict:
        if not s.get("evaluations"):
            s["recommendation"] = s["options"][0]["label"] if s["options"] else None
            s["confidence"] = "low"
            return s

        sorted_opts = sorted(s["evaluations"], key=lambda x: x["score"], reverse=True)
        best = sorted_opts[0] if sorted_opts else None
        s["recommendation"] = best["label"] if best else None

        max_score = best["score"] if best else 0
        if max_score >= 8:
            s["confidence"] = "high"
        elif max_score >= 4:
            s["confidence"] = "medium"
        else:
            s["confidence"] = "low"

        if s["confidence"] == "low":
            s["escalate"] = True
            s["reasoning"] = f"Low confidence ({max_score}/10) — escalate for user input"
        else:
            s["escalate"] = False
            s["reasoning"] = f"Recommended: {s['recommendation']} (score: {max_score}/10, confidence: {s['confidence']})"
        return s

    def _validate(self, s: Dict) -> Dict:
        risks = []
        for opt in s["options"]:
            r = opt.get("risk", "medium")
            if r == "high":
                risks.append({"risk": f"{opt.get('label')} has high risk", "severity": "high", "mitigation": "Consider alternatives"})
            elif r == "critical":
                risks.append({"risk": f"{opt.get('label')} has critical risk", "severity": "critical", "mitigation": "Do not proceed without user approval"})
        s["risks"] = risks
        if any(r["severity"] == "critical" for r in risks):
            s["escalate"] = True
        return s

    def _execute(self, s: Dict) -> Dict:
        s["executable"] = not s["escalate"]
        s["requires_approval"] = s["decision_type"] in (DecisionType.STRATEGIC, DecisionType.ARCHITECTURAL) or s["confidence"] == "low"
        return s

    def assess_risk(self, description: str, impact: float = 0.5, likelihood: float = 0.5) -> Dict:
        score = impact * likelihood
        if score >= 0.8:
            level = RiskLevel.CRITICAL
        elif score >= 0.6:
            level = RiskLevel.HIGH
        elif score >= 0.3:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        return {"description": description, "impact": impact, "likelihood": likelihood, "score": round(score, 2), "level": level.value}

    def get_history(self, limit: int = 10) -> List[Dict]:
        return self.history[-limit:]
