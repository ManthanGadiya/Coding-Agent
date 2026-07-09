from typing import Dict, Optional
from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage

SYSTEM_PROMPT = """You are a senior technical planner. Given a goal or requirements,
produce detailed plans, roadmaps, effort estimates, risk analyses,
and task decompositions. Be specific and actionable."""


class PlannerAgent(BaseAgent):
    def __init__(self, agent_id: str = "planner-1", config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            name="Planner Agent",
            capabilities=[
                "research", "requirement_analysis", "task_decomposition",
                "plan_generation", "risk_analysis", "effort_estimation",
                "roadmap_creation", "technology_comparison", "knowledge_evaluation",
            ],
            config=config
        )

    async def process_task(self, task: AgentTask) -> AgentResult:
        t = task.task_type
        if t == "research":
            return await self._conduct_research(task.input_data)
        elif t == "requirement_analysis":
            return await self._analyze_requirements(task.input_data)
        elif t == "task_decomposition":
            return await self._decompose_tasks(task.input_data)
        elif t == "plan_generation":
            return await self._generate_plan(task.input_data)
        elif t == "risk_analysis":
            return await self._analyze_risks(task.input_data)
        elif t == "effort_estimation":
            return await self._estimate_effort(task.input_data)
        elif t == "roadmap_creation":
            return await self._create_roadmap(task.input_data)
        else:
            return AgentResult(
                task_id=task.task_id, success=False,
                error=f"Planner cannot handle: {t}"
            )

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        return AgentMessage(
            sender=self.agent_id, receiver=message.sender,
            content=f"Planner: analyzed '{message.content[:50]}'",
            message_type="response"
        )

    async def _conduct_research(self, data: Dict) -> AgentResult:
        prompt = f"Research the following topic and provide findings:\nTopic: {data.get('topic', '')}\nSources: {data.get('sources', [])}\nDepth: {data.get('depth', 'moderate')}"
        output = await self._llm_generate(prompt, SYSTEM_PROMPT, max_tokens=2048)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output,
            metadata={"sources_consulted": len(data.get("sources", [])) if data.get("sources") else 2}
        )

    async def _analyze_requirements(self, data: Dict) -> AgentResult:
        prompt = f"Analyze these requirements and provide a structured breakdown:\nDescription: {data.get('description', '')}\nRequirements: {data.get('requirements', [])}\nConstraints: {data.get('constraints', [])}\nDependencies: {data.get('dependencies', [])}"
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output
        )

    async def _decompose_tasks(self, data: Dict) -> AgentResult:
        prompt = f"Decompose this goal into specific, actionable tasks:\nGoal: {data.get('goal', '')}\nComplexity: {data.get('complexity', 3)}\nProvide task IDs, descriptions, dependencies, and effort estimates."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output
        )

    async def _generate_plan(self, data: Dict) -> AgentResult:
        prompt = f"Create a detailed execution plan:\nObjective: {data.get('objective', '')}\nSteps: {data.get('steps', [])}\nInclude timeline, risks, and completion criteria."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output
        )

    async def _analyze_risks(self, data: Dict) -> AgentResult:
        prompt = f"Analyze risks for this plan:\n{data.get('plan', {})}\nIdentify technical, schedule, and knowledge risks with mitigations."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output
        )

    async def _estimate_effort(self, data: Dict) -> AgentResult:
        prompt = f"Estimate effort for these tasks:\n{data.get('tasks', [])}\nProvide total days, per-phase breakdown, and confidence levels."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output
        )

    async def _create_roadmap(self, data: Dict) -> AgentResult:
        prompt = f"Create a roadmap with milestones:\nMilestones: {data.get('milestones', ['Research', 'Implementation', 'Testing', 'Deployment'])}\nDuration: durations and dependencies."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id=data.get("task_id", ""), success=True, output=output
        )
