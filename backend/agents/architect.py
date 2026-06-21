from typing import Any, Dict, List, Optional
from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage


class ArchitectAgent(BaseAgent):
    def __init__(self, agent_id: str = "architect-1", config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            name="Architect Agent",
            capabilities=[
                "architecture_design", "technology_selection", "tradeoff_analysis",
                "risk_assessment", "scalability_evaluation", "architecture_review",
                "system_design", "dependency_analysis", "design_review",
            ],
            config=config
        )

    async def process_task(self, task: AgentTask) -> AgentResult:
        t = task.task_type
        if t == "architecture_design":
            return self._design_architecture(task.input_data)
        elif t == "technology_selection":
            return self._select_technology(task.input_data)
        elif t == "tradeoff_analysis":
            return self._analyze_tradeoffs(task.input_data)
        elif t == "risk_assessment":
            return self._assess_risks(task.input_data)
        elif t == "scalability_evaluation":
            return self._evaluate_scalability(task.input_data)
        elif t == "architecture_review":
            return self._review_architecture(task.input_data)
        else:
            return AgentResult(
                task_id=task.task_id, success=False,
                error=f"Architect cannot handle: {t}"
            )

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        return AgentMessage(
            sender=self.agent_id, receiver=message.sender,
            content=f"Architect: reviewed request '{message.content[:50]}'",
            message_type="response"
        )

    def _design_architecture(self, data: Dict) -> AgentResult:
        requirements = data.get("requirements", "")
        constraints = data.get("constraints", [])
        tech_stack = data.get("tech_stack", [])

        components = []
        if "api" in requirements.lower() or "web" in requirements.lower():
            components.append("api_gateway")
            components.append("web_server")
        if "database" in requirements.lower() or "store" in requirements.lower():
            components.append("database_layer")
        if "auth" in requirements.lower() or "user" in requirements.lower():
            components.append("auth_service")

        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "architecture": {
                    "pattern": "modular_monolith" if len(components) < 5 else "microservices",
                    "components": components,
                    "tech_stack": tech_stack or ["fastapi", "sqlalchemy", "nextjs"],
                    "recommendations": ["Use modular monolith by default, extract services when justified"],
                },
                "tradeoffs": [
                    {"decision": "monolith_vs_microservices", "rationale": "Modular monolith reduces complexity until scale demands splitting"},
                ],
                "risks": [
                    {"risk": "Tech stack lock-in", "likelihood": 0.3, "impact": 0.5},
                ],
            },
            metadata={"component_count": len(components), "requirements_analyzed": bool(requirements)}
        )

    def _select_technology(self, data: Dict) -> AgentResult:
        options = data.get("options", [])
        criteria = data.get("criteria", ["maintainability", "performance", "community"])

        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "recommendation": options[0] if options else "Use proven technologies over novel ones",
                "evaluation": {c: 0.8 for c in criteria},
                "rationale": "Prefer technologies with strong community, good DX, and proven reliability",
            },
            metadata={"options_evaluated": len(options)}
        )

    def _analyze_tradeoffs(self, data: Dict) -> AgentResult:
        decisions = data.get("decisions", [])
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "analysis": [
                    {
                        "decision": d,
                        "benefits": ["maintainability", "scalability"],
                        "costs": ["complexity", "learning curve"],
                        "recommendation": "proceed" if i % 2 == 0 else "reconsider"
                    }
                    for i, d in enumerate(decisions)
                ] if decisions else [{"message": "No decisions to analyze"}]
            },
            metadata={"decisions_analyzed": len(decisions)}
        )

    def _assess_risks(self, data: Dict) -> AgentResult:
        architecture = data.get("architecture", "")
        components = data.get("components", [])
        risks = []
        if not architecture:
            risks.append({"risk": "No architecture defined", "severity": "high", "mitigation": "Define architecture before implementation"})
        if len(components) > 7:
            risks.append({"risk": "High component count increases coordination complexity", "severity": "medium", "mitigation": "Consider merging related components"})

        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "risks": risks or [{"risk": "No significant risks identified", "severity": "low"}],
                "overall_risk": "low" if not risks else "medium",
            }
        )

    def _evaluate_scalability(self, data: Dict) -> AgentResult:
        components = data.get("components", [])
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "scalability": "modular_monolith_sufficient" if len(components) < 5 else "microservices_recommended",
                "bottlenecks": ["database" if "database" in components else "none identified"],
                "recommendations": ["Add caching layer", "Use connection pooling", "Horizontal scaling when traffic grows"],
            }
        )

    def _review_architecture(self, data: Dict) -> AgentResult:
        proposal = data.get("proposal", {})
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "status": "approved" if proposal else "needs_definition",
                "findings": [],
                "recommendations": ["Ensure each component has single responsibility", "Document all interfaces"],
            }
        )
