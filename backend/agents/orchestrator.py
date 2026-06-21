from typing import Any, Dict, List, Optional, Type
import asyncio
from datetime import datetime

from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage, AgentState
from backend.agents.coder import CoderAgent
from backend.agents.reviewer import ReviewerAgent
from backend.agents.tester import TesterAgent
from backend.agents.memory import MemoryAgent
from backend.agents.debugger import DebuggerAgent


class OrchestratorAgent(BaseAgent):
    def __init__(self, agent_id: str = "orchestrator-1", config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            name="Orchestrator Agent",
            capabilities=[
                "route_task", "assign_agent", "monitor_progress",
                "resolve_conflict", "manage_workflow", "report_status",
                "classify_task", "assess_complexity"
            ],
            config=config
        )
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, Dict] = {}
        self._init_default_agents()

    def _init_default_agents(self):
        defaults = {
            "coder-1": CoderAgent(),
            "reviewer-1": ReviewerAgent(),
            "tester-1": TesterAgent(),
            "memory-1": MemoryAgent(),
            "debugger-1": DebuggerAgent(),
        }
        for agent_id, agent in defaults.items():
            self.register_agent(agent)

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def find_agents_for_task(self, task_type: str) -> List[BaseAgent]:
        return [a for a in self.agents.values() if a.can_handle(task_type)]

    async def process_task(self, task: AgentTask) -> AgentResult:
        task_type = task.task_type

        if task_type == "route_task":
            return await self._route_task(task.input_data)
        elif task_type == "assign_agent":
            return await self._assign_agent(task.input_data)
        elif task_type == "monitor_progress":
            return self._monitor_progress(task.input_data)
        elif task_type == "resolve_conflict":
            return await self._resolve_conflict(task.input_data)
        elif task_type == "manage_workflow":
            return await self._manage_workflow(task.input_data)
        elif task_type == "report_status":
            return self._report_status(task.input_data)
        elif task_type == "classify_task":
            return self._classify_task(task.input_data)
        elif task_type == "assess_complexity":
            return self._assess_complexity(task.input_data)
        else:
            # Try to route to capable agent
            candidates = self.find_agents_for_task(task_type)
            if candidates:
                return await candidates[0].execute_task(task)
            return AgentResult(
                task_id=task.task_id,
                success=False,
                error=f"No agent can handle task type: {task_type}"
            )

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        if message.message_type == "query":
            statuses = {aid: a.state.value for aid, a in self.agents.items()}
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=f"Orchestrator managing {len(self.agents)} agents. Status: {statuses}",
                message_type="response"
            )
        elif message.receiver in self.agents:
            target = self.agents[message.receiver]
            await target.message_queue.put(message)
        return None

    async def _route_task(self, data: Dict) -> AgentResult:
        task_type = data.get("task_type", "")
        description = data.get("description", "")

        complexity = self._assess_complexity({"description": description})
        agents = self.find_agents_for_task(task_type)

        if not agents:
            return AgentResult(
                task_id="",
                success=False,
                error=f"No agent for {task_type}",
                output={"available_agents": list(self.agents.keys())}
            )

        return AgentResult(
            task_id="",
            success=True,
            output={
                "assigned_agent": agents[0].agent_id,
                "agent_count": len(agents),
                "complexity": complexity.output
            },
            metadata={"task_type": task_type, "agent": agents[0].agent_id}
        )

    async def _assign_agent(self, data: Dict) -> AgentResult:
        agent_id = data.get("agent_id")
        task_data = data.get("task", {})

        agent = self.get_agent(agent_id)
        if not agent:
            return AgentResult(task_id="", success=False, error=f"Agent {agent_id} not found")

        task = AgentTask(
            task_id=task_data.get("task_id", ""),
            task_type=task_data.get("task_type", ""),
            description=task_data.get("description", ""),
            input_data=task_data.get("input_data", {}),
            priority=task_data.get("priority", 5)
        )

        result = await agent.execute_task(task)
        return result

    def _monitor_progress(self, data: Dict) -> AgentResult:
        return AgentResult(
            task_id="",
            success=True,
            output={
                agent_id: {
                    "state": agent.state.value,
                    "current_task": agent.current_task.task_id if agent.current_task else None,
                    "capabilities": agent.capabilities
                }
                for agent_id, agent in self.agents.items()
            },
            metadata={"agent_count": len(self.agents)}
        )

    async def _resolve_conflict(self, data: Dict) -> AgentResult:
        agents_involved = data.get("agents", [])
        issue = data.get("issue", "")
        evidence = data.get("evidence", "")

        # ponytail: simple tie-break — higher capability count wins
        resolution = None
        if len(agents_involved) == 2:
            a1 = self.get_agent(agents_involved[0])
            a2 = self.get_agent(agents_involved[1])
            if a1 and a2:
                resolution = agents_involved[0] if len(a1.capabilities) >= len(a2.capabilities) else agents_involved[1]

        return AgentResult(
            task_id="",
            success=True,
            output={
                "resolution": resolution or "needs_user_input",
                "issue": issue,
                "agents_involved": agents_involved
            },
            metadata={"resolved": resolution is not None}
        )

    async def _manage_workflow(self, data: Dict) -> AgentResult:
        workflow_id = data.get("workflow_id", str(id(data)))
        steps = data.get("steps", [])

        self.workflows[workflow_id] = {
            "steps": steps,
            "current_step": 0,
            "status": "running",
            "results": [],
            "started_at": datetime.utcnow().isoformat()
        }

        for i, step in enumerate(steps):
            self.workflows[workflow_id]["current_step"] = i
            agent = self.get_agent(step.get("agent_id"))
            if not agent:
                self.workflows[workflow_id]["status"] = "failed"
                return AgentResult(
                    task_id="",
                    success=False,
                    error=f"Step {i}: agent {step.get('agent_id')} not found",
                    metadata={"workflow_id": workflow_id, "step": i}
                )

            task = AgentTask(
                task_id=step.get("task_id", f"{workflow_id}-step-{i}"),
                task_type=step.get("task_type", ""),
                description=step.get("description", ""),
                input_data=step.get("input_data", {}),
                priority=data.get("priority", 5)
            )
            result = await agent.execute_task(task)
            self.workflows[workflow_id]["results"].append(result)

            if not result.success and step.get("critical", False):
                self.workflows[workflow_id]["status"] = "failed"
                return result

        self.workflows[workflow_id]["status"] = "completed"
        return AgentResult(
            task_id="",
            success=True,
            output={
                "workflow_id": workflow_id,
                "status": "completed",
                "steps_completed": len(steps),
                "results": [r.output for r in self.workflows[workflow_id]["results"]]
            },
            metadata={"workflow_id": workflow_id, "steps": len(steps)}
        )

    def _report_status(self, data: Dict) -> AgentResult:
        include_agents = data.get("include_agents", True)
        report = {
            "orchestrator_state": self.state.value,
            "active_workflows": len(self.workflows),
            "registered_agents": len(self.agents),
        }

        if include_agents:
            report["agents"] = {
                aid: {
                    "state": a.state.value,
                    "capabilities": a.capabilities,
                    "tasks_completed": len([r for r in a._task_history if r.success]),
                    "tasks_failed": len([r for r in a._task_history if not r.success])
                }
                for aid, a in self.agents.items()
            }

        return AgentResult(
            task_id="",
            success=True,
            output=report,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )

    def _classify_task(self, data: Dict) -> AgentResult:
        description = data.get("description", "").lower()

        if any(kw in description for kw in ["bug", "error", "fail", "broken", "crash"]):
            task_type = "debugging"
        elif any(kw in description for kw in ["test", "coverage", "validate"]):
            task_type = "testing"
        elif any(kw in description for kw in ["review", "audit", "check"]):
            task_type = "review"
        elif any(kw in description for kw in ["implement", "create", "add", "build", "write"]):
            task_type = "implementation"
        elif any(kw in description for kw in ["research", "investigate", "learn"]):
            task_type = "research"
        elif any(kw in description for kw in ["refactor", "clean", "improve"]):
            task_type = "refactoring"
        elif any(kw in description for kw in ["design", "architect", "plan"]):
            task_type = "architecture"
        else:
            task_type = "general"

        return AgentResult(
            task_id="",
            success=True,
            output={"task_type": task_type, "confidence": 0.7 if task_type != "general" else 0.3},
            metadata={"classifier": "rule-based"}
        )

    def _assess_complexity(self, data: Dict) -> AgentResult:
        description = data.get("description", "")
        lines = len(description.split("\n"))
        word_count = len(description.split())

        if word_count < 10:
            level = 1
        elif word_count < 50:
            level = 2
        elif word_count < 200:
            level = 3
        else:
            level = 4

        labels = {1: "simple", 2: "moderate", 3: "complex", 4: "project"}

        return AgentResult(
            task_id="",
            success=True,
            output={"level": level, "label": labels[level]},
            metadata={"word_count": word_count, "algorithm": "heuristic"}
        )

    async def run_workflow(self, workflow_id: str, steps: List[Dict]) -> AgentResult:
        return await self._manage_workflow({"workflow_id": workflow_id, "steps": steps})