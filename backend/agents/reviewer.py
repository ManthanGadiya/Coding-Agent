from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage


class ReviewerAgent(BaseAgent):
    def __init__(self, agent_id: str = "reviewer-1", config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            name="Reviewer Agent",
            capabilities=[
                "review_code", "review_architecture", "review_security",
                "review_maintainability", "review_complexity", "approve", "reject"
            ],
            config=config
        )

    async def process_task(self, task: AgentTask) -> AgentResult:
        task_type = task.task_type
        data = task.input_data

        if task_type == "review_code":
            return self._review_code(data)
        elif task_type == "review_architecture":
            return self._review_architecture(data)
        elif task_type == "review_security":
            return self._review_security(data)
        elif task_type == "review_maintainability":
            return self._review_maintainability(data)
        elif task_type in ("approve", "reject"):
            return self._make_decision(task_type, data)
        else:
            return AgentResult(
                task_id=task.task_id,
                success=False,
                error=f"Unknown review type: {task_type}"
            )

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        if message.message_type == "query":
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=f"ReviewerAgent ready. Capabilities: {', '.join(self.capabilities)}",
                message_type="response"
            )
        return None

    def _review_code(self, data: Dict) -> AgentResult:
        path = data.get("path")
        content = data.get("content", "")
        findings = []

        if not content and path:
            try:
                content = open(path).read()
            except:
                findings.append({"severity": "error", "message": f"Cannot read {path}"})

        lines = content.split("\n") if content else []

        # Basic static analysis
        if any("TODO" in l or "FIXME" in l for l in lines):
            findings.append({"severity": "warning", "category": "maintainability", "message": "Contains TODO/FIXME markers"})

        if "import *" in content:
            findings.append({"severity": "warning", "category": "style", "message": "Wildcard imports harm readability"})

        if len(lines) > 500:
            findings.append({"severity": "info", "category": "complexity", "message": f"File has {len(lines)} lines, consider splitting"})

        # ponytail: basic file-level checks, deep review uses LLM pass
        score = max(0, 10 - len(findings))
        return AgentResult(
            task_id="",
            success=True,
            output={"findings": findings, "score": score, "lines_analyzed": len(lines)},
            metadata={"path": path, "finding_count": len(findings)}
        )

    def _review_architecture(self, data: Dict) -> AgentResult:
        structure = data.get("structure", {})
        violations = []

        if "imports" in structure:
            for imp in structure["imports"]:
                if imp.get("from", "").startswith("backend."):
                    parts = imp["from"].split(".")
                    # ponytail: simple layer check, expand as needed
                    if len(parts) > 3:
                        violations.append({
                            "severity": "info",
                            "message": f"Deep import chain: {imp['from']}"
                        })

        return AgentResult(
            task_id="",
            success=True,
            output={"violations": violations, "compliant": len(violations) == 0},
            metadata={"violation_count": len(violations)}
        )

    def _review_security(self, data: Dict) -> AgentResult:
        content = data.get("content", "")
        risks = []

        secrets = ["api_key", "password", "secret", "token", "credential"]
        for secret in secrets:
            if secret in content.lower() and "=" in content.lower().split(secret)[-1][:20]:
                risks.append({"severity": "high", "category": "secrets", "message": f"Potential {secret} in code"})

        if "eval(" in content or "exec(" in content:
            risks.append({"severity": "high", "category": "code_injection", "message": "Dynamic code execution detected"})

        if "subprocess.run" in content and "shell=True" in content:
            risks.append({"severity": "high", "category": "command_injection", "message": "Shell execution with shell=True"})

        return AgentResult(
            task_id="",
            success=len([r for r in risks if r["severity"] == "high"]) == 0,
            output={"risks": risks, "safe": len(risks) == 0},
            metadata={"risk_count": len(risks)}
        )

    def _review_maintainability(self, data: Dict) -> AgentResult:
        content = data.get("content", "")
        issues = []

        if not content.strip():
            return AgentResult(task_id="", success=True, output={"issues": [], "score": 10})

        lines = content.split("\n")
        long_lines = [i+1 for i, l in enumerate(lines) if len(l) > 120]
        if long_lines:
            issues.append({"severity": "warning", "message": f"{len(long_lines)} lines exceed 120 chars"})

        # ponytail: basic maintainability checks
        return AgentResult(
            task_id="",
            success=True,
            output={"issues": issues, "score": max(0, 10 - len(issues))}
        )

    def _make_decision(self, decision: str, data: Dict) -> AgentResult:
        return AgentResult(
            task_id="",
            success=True,
            output={"decision": decision, "reason": data.get("reason", "")},
            metadata={"decision": decision}
        )