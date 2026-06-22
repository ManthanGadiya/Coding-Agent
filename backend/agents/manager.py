from typing import Any, Dict, List, Optional, Type
import asyncio
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage, AgentState
from backend.core.workflow_engine import ComplexityLevel, workflow_controller
from backend.agents.coder import CoderAgent
from backend.agents.reviewer import ReviewerAgent
from backend.agents.tester import TesterAgent
from backend.agents.memory import MemoryAgent
from backend.agents.debugger import DebuggerAgent
from backend.agents.architect import ArchitectAgent
from backend.agents.planner import PlannerAgent


class ConflictStep(str, Enum):
    IDENTIFIED = "identified"
    DIRECT_DISCUSSION = "direct_discussion"
    EVIDENCE_EXCHANGE = "evidence_exchange"
    CONSENSUS_ATTEMPT = "consensus_attempt"
    MANAGER_ARBITRATION = "manager_arbitration"
    USER_ESCALATION = "user_escalation"


class ConflictSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConflictRecord:
    conflict_id: str
    agents_involved: List[str]
    topic: str
    severity: ConflictSeverity
    current_step: ConflictStep = ConflictStep.IDENTIFIED
    evidence: Dict[str, str] = field(default_factory=dict)
    arguments: Dict[str, str] = field(default_factory=dict)
    resolution: Optional[str] = None
    reasoning: Optional[str] = None
    outcome: Optional[str] = None
    lessons: List[str] = field(default_factory=list)
    created_at: str = ""
    resolved_at: Optional[str] = None


DISALLOWED_COMMUNICATION_PATHS = {
    ("reviewer", "architect"): "Reviewer→Architect must go through Manager",
    ("debugger", "architect"): "Debugger→Architect must go through Manager",
    ("coder", "firecrawl"): "Coder cannot use research tools directly — use Planner",
    ("coder", "web_research"): "Coder cannot do independent research — use Planner",
}


class ManagerAgent(BaseAgent):
    def __init__(self, agent_id: str = "manager-1", config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            name="Manager Agent",
            capabilities=[
                "route_task", "assign_agent", "monitor_progress",
                "resolve_conflict", "manage_workflow", "report_status",
                "classify_task", "assess_complexity"
            ],
            config=config
        )
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, Dict] = {}
        self.conflict_records: List[ConflictRecord] = []
        self._init_default_agents()

    def _init_default_agents(self):
        defaults = {
            "coder-1": CoderAgent(),
            "reviewer-1": ReviewerAgent(),
            "tester-1": TesterAgent(),
            "memory-1": MemoryAgent(),
            "debugger-1": DebuggerAgent(),
            "architect-1": ArchitectAgent(),
            "planner-1": PlannerAgent(),
        }
        for agent_id, agent in defaults.items():
            self.register_agent(agent)

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def find_agents_for_task(self, task_type: str) -> List[BaseAgent]:
        return [a for a in self.agents.values() if a.can_handle(task_type)]

    STEP_TASK_MAP: Dict[str, str] = {
        "manager_analysis": "classify_task", "workflow_selection": "route_task",
        "feature_classification": "classify_task", "bug_classification": "classify_task",
        "refactor_classification": "classify_task", "agent_assignment": "assign_agent",
        "manager_approval": "route_task", "manager_decision": "route_task",
        "requirements": "requirement_analysis", "research": "research",
        "architecture": "architecture_design", "planning": "plan_generation",
        "implementation": "implement", "testing": "run_test",
        "validation": "run_test", "regression_testing": "run_test",
        "review": "review_code", "memory_update": "store",
        "knowledge_capture": "store", "investigation": "diagnose",
        "root_cause_analysis": "analyze_error", "quality_gate": "route_task",
        "user_awareness": "route_task", "release_execution": "route_task",
        "monitoring": "run_test", "post_release_review": "review_code",
        "test_validation": "run_test", "review_validation": "review_code",
    }

    AGENT_NAME_MAP: Dict[str, str] = {
        "manager": "manager-1", "planner": "planner-1", "architect": "architect-1",
        "coder": "coder-1", "tester": "tester-1", "debugger": "debugger-1",
        "reviewer": "reviewer-1", "memory": "memory-1",
    }

    async def run_goal(self, goal: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        goal_context = context or {}
        classification = self._classify_task({"description": goal})
        task_type = classification.output["task_type"]
        complexity = self._assess_complexity({"description": goal})
        complexity_label = complexity.output["label"]
        level_map = {"simple": "simple", "moderate": "moderate", "complex": "complex", "project": "critical"}
        complexity_enum = ComplexityLevel(level_map.get(complexity_label, "moderate"))
        category = workflow_controller.enforce_smallest_workflow("task_pipeline", complexity_enum)
        pipeline = workflow_controller.create_pipeline(category, complexity_enum.value)
        results: List[Dict[str, Any]] = []
        for i, step_def in enumerate(pipeline.steps):
            agent_name = step_def["agent"]
            agent_id = self.AGENT_NAME_MAP.get(agent_name)
            agent = self.get_agent(agent_id) if agent_id else None
            if not agent:
                step_result = {"step": step_def["name"], "agent": agent_name, "status": "failed", "error": f"No agent mapped for role: {agent_name}"}
                workflow_controller.transition(pipeline.id, {"status": "failed", "error": step_result["error"]})
                results.append(step_result)
                break
            task_type_for_step = self.STEP_TASK_MAP.get(step_def["name"], "general")
            task = AgentTask(
                task_id=f"{pipeline.id}-step-{i}",
                task_type=task_type_for_step,
                description=step_def["description"],
                input_data={"goal": goal, "task_type": task_type, "complexity": complexity_label, "context": goal_context, "step": step_def},
            )
            result = await agent.execute_task(task)
            step_result = {"step": step_def["name"], "agent": agent_id, "status": "completed" if result.success else "failed", "task_type": task_type_for_step, "output": str(result.output)[:500], "error": result.error}
            results.append(step_result)
            workflow_controller.transition(pipeline.id, {"status": "completed" if result.success else "failed", "output": result.output, "error": result.error})
            if not result.success:
                break
        pipeline_status = workflow_controller.get_status(pipeline.id)
        return {
            "goal": goal, "classification": task_type, "complexity": complexity_label,
            "pipeline_id": pipeline.id,
            "pipeline_status": pipeline_status.state.value if pipeline_status else "unknown",
            "steps": results, "success": all(r["status"] == "completed" for r in results),
            "total_steps": len(pipeline.steps), "completed_steps": len([r for r in results if r["status"] == "completed"]),
        }

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
                content=f"Manager managing {len(self.agents)} agents. Status: {statuses}",
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

    def check_communication_path(self, sender: str, receiver: str) -> Optional[str]:
        key = (sender, receiver)
        if key in DISALLOWED_COMMUNICATION_PATHS:
            return DISALLOWED_COMMUNICATION_PATHS[key]
        return None

    async def _resolve_conflict(self, data: Dict) -> AgentResult:
        agents_involved = data.get("agents", [])
        issue = data.get("issue", "")
        arguments = data.get("arguments", {})

        conflict_id = f"conflict-{len(self.conflict_records) + 1}"
        record = ConflictRecord(
            conflict_id=conflict_id,
            agents_involved=agents_involved,
            topic=issue,
            severity=ConflictSeverity(data.get("severity", "medium")),
            arguments=arguments,
            created_at=datetime.utcnow().isoformat(),
        )

        # Step 1-2: Direct Discussion + Evidence Exchange
        record.current_step = ConflictStep.DIRECT_DISCUSSION
        scores = {}
        for agent_id in agents_involved:
            agent = self.get_agent(agent_id)
            if agent:
                arg = arguments.get(agent_id, "")
                scores[agent_id] = {
                    "argument_quality": min(len(arg) / 200, 1.0),
                    "capability_count": len(agent.capabilities),
                    "has_evidence": bool(data.get(f"evidence_{agent_id}", "")),
                }

        # Step 3: Consensus Attempt
        record.current_step = ConflictStep.EVIDENCE_EXCHANGE
        if len(agents_involved) == 2 and scores:
            a1, a2 = agents_involved[0], agents_involved[1]
            s1 = scores.get(a1, {})
            s2 = scores.get(a2, {})
            score1 = s1.get("argument_quality", 0) + s1.get("capability_count", 0) * 0.1
            score2 = s2.get("argument_quality", 0) + s2.get("capability_count", 0) * 0.1

            # Step 4: Consensus attempt — within 20% is close enough
            record.current_step = ConflictStep.CONSENSUS_ATTEMPT
            max_score = max(score1, score2)
            min_score = min(score1, score2)
            if max_score > 0 and (max_score - min_score) / max_score < 0.2:
                record.resolution = "consensus"
                record.reasoning = "Agents reached consensus through evidence exchange"
                record.outcome = "resolved"
            else:
                # Step 5: Manager Arbitration
                record.current_step = ConflictStep.MANAGER_ARBITRATION
                winner = a1 if score1 >= score2 else a2
                record.resolution = winner
                record.reasoning = (
                    f"Manager arbitration: {winner} won on evidence strength "
                    f"({score1:.2f} vs {score2:.2f})"
                )
                record.outcome = "resolved"

                # Step 6: User Escalation if unresolved
                if data.get("escalate", False) or record.severity == ConflictSeverity.CRITICAL:
                    record.current_step = ConflictStep.USER_ESCALATION
                    record.outcome = "escalated_to_user"

        record.resolved_at = datetime.utcnow().isoformat()
        self.conflict_records.append(record)

        return AgentResult(
            task_id="",
            success=True,
            output={
                "conflict_id": conflict_id,
                "resolution": record.resolution,
                "outcome": record.outcome,
                "step": record.current_step.value,
                "issue": issue,
                "agents_involved": agents_involved,
            },
            metadata={"resolved": record.outcome == "resolved", "severity": record.severity.value}
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
            "manager_state": self.state.value,
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