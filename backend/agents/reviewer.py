from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage

SYSTEM_PROMPT = """You are a senior code reviewer. Analyze code for bugs,
security issues, maintainability problems, and design flaws.
Be specific, cite line numbers, and suggest concrete fixes."""


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
            return await self._review_code(data)
        elif task_type == "review_architecture":
            return await self._review_architecture(data)
        elif task_type == "review_security":
            return await self._review_security(data)
        elif task_type == "review_maintainability":
            return await self._review_maintainability(data)
        elif task_type in ("approve", "reject"):
            return await self._make_decision(task_type, data)
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

    async def _review_code(self, data: Dict) -> AgentResult:
        path = data.get("path")
        content = data.get("content", "")
        if not content and path:
            try:
                content = open(path).read()
            except:
                content = ""
        lines = content.split("\n") if content else []
        # ponytail: static analysis for quick wins, LLM for deep review
        findings = []
        if any("TODO" in l or "FIXME" in l for l in lines):
            findings.append("Contains TODO/FIXME markers")
        if "import *" in content:
            findings.append("Wildcard imports harm readability")
        if len(lines) > 500:
            findings.append(f"File has {len(lines)} lines, consider splitting")
        prompt = f"Review this code at {path or 'unknown'}:\n\n{content}\n\nFindings so far: {findings}\n\nProvide a full review with specific issues and fixes."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT, max_tokens=2048)
        return AgentResult(
            task_id="", success=True,
            output={"llm_review": output, "static_findings": findings, "lines_analyzed": len(lines)},
            metadata={"path": path, "finding_count": len(findings)}
        )

    async def _review_architecture(self, data: Dict) -> AgentResult:
        prompt = f"Review this architecture:\nStructure: {data.get('structure', {})}\nEvaluate layer violations, coupling, and design patterns."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True, output=output,
            metadata={}
        )

    async def _review_security(self, data: Dict) -> AgentResult:
        content = data.get("content", "")
        risks = []
        secrets = ["api_key", "password", "secret", "token", "credential"]
        for secret in secrets:
            if secret in content.lower() and "=" in content.lower().split(secret)[-1][:20]:
                risks.append(f"Potential {secret} in code")
        if "eval(" in content or "exec(" in content:
            risks.append("Dynamic code execution detected")
        if "subprocess.run" in content and "shell=True" in content:
            risks.append("Shell execution with shell=True")
        # ponytail: static pattern check first, LLM for deeper analysis
        prompt = f"Review this code for security vulnerabilities:\n\n{content}\n\nStatic findings so far: {risks}\nIdentify all security issues with severity levels."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True,
            output={"llm_review": output, "static_risks": risks, "safe": len(risks) == 0},
            metadata={"risk_count": len(risks)}
        )

    async def _review_maintainability(self, data: Dict) -> AgentResult:
        content = data.get("content", "")
        lines = content.split("\n") if content else []
        issues = []
        if not content.strip():
            return AgentResult(task_id="", success=True, output={"issues": [], "score": 10})
        long_lines = [i+1 for i, l in enumerate(lines) if len(l) > 120]
        if long_lines:
            issues.append(f"{len(long_lines)} lines exceed 120 chars")
        prompt = f"Review this code for maintainability:\n\n{content}\n\nLine-length issues: {issues}\nAssess overall maintainability and suggest improvements."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True,
            output={"llm_review": output, "static_issues": issues, "score": max(0, 10 - len(issues))}
        )

    async def _make_decision(self, decision: str, data: Dict) -> AgentResult:
        prompt = f"Review this and provide a {'approval' if decision == 'approve' else 'rejection'} rationale:\n{data.get('reason', '')}\nContext: {data.get('context', '')}"
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True,
            output={"decision": decision, "rationale": output},
            metadata={"decision": decision}
        )
