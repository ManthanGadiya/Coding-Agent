from typing import Any, Dict, List, Optional
from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage


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
            return self._conduct_research(task.input_data)
        elif t == "requirement_analysis":
            return self._analyze_requirements(task.input_data)
        elif t == "task_decomposition":
            return self._decompose_tasks(task.input_data)
        elif t == "plan_generation":
            return self._generate_plan(task.input_data)
        elif t == "risk_analysis":
            return self._analyze_risks(task.input_data)
        elif t == "effort_estimation":
            return self._estimate_effort(task.input_data)
        elif t == "roadmap_creation":
            return self._create_roadmap(task.input_data)
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

    def _conduct_research(self, data: Dict) -> AgentResult:
        topic = data.get("topic", "")
        sources = data.get("sources", [])
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "topic": topic,
                "findings": [
                    {"source": s, "key_points": [f"Research finding from {s}"], "confidence": 0.7}
                    for s in (sources or ["documentation", "web_search"])
                ],
                "summary": f"Research on '{topic}' completed." if topic else "No topic specified.",
                "knowledge_value": "high" if topic else "none",
            },
            metadata={"sources_consulted": len(sources) if sources else 2}
        )

    def _analyze_requirements(self, data: Dict) -> AgentResult:
        description = data.get("description", "")
        requirements = data.get("requirements", [])
        risks = []
        if not description and not requirements:
            risks.append("No requirements provided — risk of misunderstanding")
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "goals": [description] if description else [],
                "constraints": data.get("constraints", []),
                "dependencies": data.get("dependencies", []),
                "risks": risks,
                "assumptions": ["Requirements are complete and accurate unless contradicted"],
                "unknowns": ["Edge cases", "Performance requirements"] if not requirements else [],
                "success_criteria": ["All requirements implemented", "Tests pass", "Review approved"],
            }
        )

    def _decompose_tasks(self, data: Dict) -> AgentResult:
        goal = data.get("goal", "")
        complexity = data.get("complexity", 3)
        task_count = min(complexity + 1, 8)
        tasks = [
            {
                "id": f"TASK-{i+1}",
                "title": f"{'Research' if i == 0 else 'Implement' if i == 1 else 'Test' if i == 2 else 'Review' if i == 3 else 'Document' if i == 4 else f'Step {i+1}'} - {goal[:30]}",
                "description": f"Sub-task {i+1} of '{goal}'",
                "dependencies": [f"TASK-{j}" for j in range(1, i)],
                "estimated_effort": f"{i+1}d",
            }
            for i in range(task_count)
        ]
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "milestones": [
                    {"name": "Research Complete", "tasks": [t["id"] for t in tasks[:1]]},
                    {"name": "Implementation Done", "tasks": [t["id"] for t in tasks[1:3]]},
                    {"name": "Quality Verified", "tasks": [t["id"] for t in tasks[3:]]},
                ],
                "tasks": tasks,
                "total_estimated_days": sum(int(t["estimated_effort"][:-1]) for t in tasks),
            }
        )

    def _generate_plan(self, data: Dict) -> AgentResult:
        objective = data.get("objective", "")
        steps = data.get("steps", [])
        if not steps:
            steps = [
                "1. Research and gather requirements",
                "2. Design architecture",
                "3. Implement core functionality",
                "4. Write and run tests",
                "5. Review and refactor",
                "6. Deploy and monitor",
            ]
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "objective": objective,
                "plan": steps,
                "risks": ["Scope creep", "Unforeseen dependencies"],
                "estimated_effort": f"{len(steps) * 2}d",
                "completion_criteria": ["All steps completed", "Tests passing", "Review approved"],
            }
        )

    def _analyze_risks(self, data: Dict) -> AgentResult:
        plan = data.get("plan", {})
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "risks": [
                    {"type": "technical", "description": "Unknown technology stack", "likelihood": 0.4, "impact": 0.6, "mitigation": "Prototype before full implementation"},
                    {"type": "schedule", "description": "Underestimated complexity", "likelihood": 0.5, "impact": 0.5, "mitigation": "Add buffer time"},
                    {"type": "knowledge", "description": "New domain", "likelihood": 0.3, "impact": 0.7, "mitigation": "Research phase first"},
                ],
                "overall_risk_score": 0.4,
            }
        )

    def _estimate_effort(self, data: Dict) -> AgentResult:
        tasks = data.get("tasks", [])
        total = len(tasks) * 2 if tasks else 5
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "total_days": total,
                "confidence": 0.6,
                "breakdown": [
                    {"phase": "Research", "days": 1, "confidence": 0.7},
                    {"phase": "Implementation", "days": max(1, total // 2), "confidence": 0.5},
                    {"phase": "Testing", "days": max(1, total // 4), "confidence": 0.6},
                    {"phase": "Review", "days": 1, "confidence": 0.8},
                ],
            }
        )

    def _create_roadmap(self, data: Dict) -> AgentResult:
        milestones = data.get("milestones", ["Research", "Implementation", "Testing", "Deployment"])
        return AgentResult(
            task_id=data.get("task_id", ""), success=True,
            output={
                "roadmap": [
                    {"milestone": m, "order": i, "duration": f"{i+1}w", "dependencies": milestones[:i] if i > 0 else []}
                    for i, m in enumerate(milestones)
                ],
                "total_duration": f"{len(milestones)}w",
            }
        )
