from typing import Dict, Optional
from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage

SYSTEM_PROMPT = """You are a senior software architect. Given requirements and context,
produce architecture designs, technology recommendations, tradeoff analyses,
risk assessments, and scalability evaluations. Be specific and practical."""


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
            return await self._design_architecture(task.input_data)
        elif t == "technology_selection":
            return await self._select_technology(task.input_data)
        elif t == "tradeoff_analysis":
            return await self._analyze_tradeoffs(task.input_data)
        elif t == "risk_assessment":
            return await self._assess_risks(task.input_data)
        elif t == "scalability_evaluation":
            return await self._evaluate_scalability(task.input_data)
        elif t == "architecture_review":
            return await self._review_architecture(task.input_data)
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

    async def _design_architecture(self, data: Dict) -> AgentResult:
        prompt = f"Design an architecture for:\nRequirements: {data.get('requirements', '')}\nConstraints: {data.get('constraints', [])}\nTech stack options: {data.get('tech_stack', [])}\n\nProvide components, patterns, and rationale."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT, max_tokens=2048)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output,
            metadata={"requirements_analyzed": bool(data.get("requirements"))}
        )

    async def _select_technology(self, data: Dict) -> AgentResult:
        prompt = f"Select the best technology from these options: {data.get('options', [])}\nCriteria: {data.get('criteria', ['maintainability', 'performance', 'community'])}\nProject context: {data.get('context', '')}"
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output,
            metadata={"options_evaluated": len(data.get("options", []))}
        )

    async def _analyze_tradeoffs(self, data: Dict) -> AgentResult:
        prompt = f"Analyze tradeoffs for these architecture decisions: {data.get('decisions', [])}\nContext: {data.get('context', '')}"
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output,
            metadata={"decisions_analyzed": len(data.get("decisions", []))}
        )

    async def _assess_risks(self, data: Dict) -> AgentResult:
        prompt = f"Assess risks for this architecture:\nArchitecture: {data.get('architecture', '')}\nComponents: {data.get('components', [])}\nTech stack: {data.get('tech_stack', [])}"
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output
        )

    async def _evaluate_scalability(self, data: Dict) -> AgentResult:
        prompt = f"Evaluate scalability for:\nComponents: {data.get('components', [])}\nExpected load: {data.get('expected_load', '')}\nConstraints: {data.get('constraints', [])}"
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output
        )

    async def _review_architecture(self, data: Dict) -> AgentResult:
        prompt = f"Review this architecture proposal:\n{data.get('proposal', {})}\nProvide findings and recommendations."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output
        )
