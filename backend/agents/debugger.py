from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage

SYSTEM_PROMPT = """You are an expert debugger. Given error messages, tracebacks,
and code context, identify root causes and suggest specific fixes.
Be precise and actionable."""


class DebuggerAgent(BaseAgent):
    def __init__(self, agent_id: str = "debugger-1", config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            name="Debugger Agent",
            capabilities=[
                "diagnose", "analyze_error", "trace",
                "check_logs", "reproduce", "suggest_fix"
            ],
            config=config
        )

    async def process_task(self, task: AgentTask) -> AgentResult:
        task_type = task.task_type
        data = task.input_data

        if task_type == "diagnose":
            return await self._diagnose(data)
        elif task_type == "analyze_error":
            return await self._analyze_error(data)
        elif task_type == "trace":
            return await self._trace(data)
        elif task_type == "check_logs":
            return await self._check_logs(data)
        elif task_type == "reproduce":
            return await self._reproduce(data)
        elif task_type == "suggest_fix":
            return await self._suggest_fix(data)
        else:
            return AgentResult(
                task_id=task.task_id,
                success=False,
                error=f"Unknown debug type: {task_type}"
            )

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        if message.message_type == "query":
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=f"DebuggerAgent ready. Capabilities: {', '.join(self.capabilities)}",
                message_type="response"
            )
        return None

    async def _diagnose(self, data: Dict) -> AgentResult:
        error = data.get("error", "")
        context = data.get("context", "")
        code_snippet = data.get("code_snippet", "")
        # ponytail: quick pattern match for common errors
        hypotheses = []
        if "KeyError" in error:
            hypotheses.append("Missing key in dict")
        if "AttributeError" in error:
            hypotheses.append("Wrong type or None access")
        if "TypeError" in error:
            hypotheses.append("Type mismatch or wrong arg count")
        if "ImportError" in error or "ModuleNotFoundError" in error:
            hypotheses.append("Missing dependency or wrong import path")
        prompt = f"Diagnose this error:\nError: {error}\nContext: {context}\nCode:\n{code_snippet}\n\nPattern matches: {hypotheses}\nProvide root cause analysis and fix."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT, max_tokens=2048)
        return AgentResult(
            task_id="", success=True,
            output={"llm_diagnosis": output, "pattern_hypotheses": hypotheses},
            metadata={"hypothesis_count": len(hypotheses)}
        )

    async def _analyze_error(self, data: Dict) -> AgentResult:
        traceback = data.get("traceback", "")
        prompt = f"Analyze this traceback and identify the root cause:\n\n{traceback}\n\nExplain what failed and why."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True, output=output,
            metadata={"traceback_length": len(traceback)}
        )

    async def _trace(self, data: Dict) -> AgentResult:
        prompt = f"Trace the execution flow for:\nPath: {data.get('path', '')}\nFunction: {data.get('function', '')}\nContext: {data.get('context', '')}\nIdentify the code path and potential issues."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True, output=output,
            metadata={"path": data.get("path", ""), "function": data.get("function", "")}
        )

    async def _check_logs(self, data: Dict) -> AgentResult:
        log_content = data.get("content", "")
        log_path = data.get("path")
        if not log_content and log_path:
            try:
                log_content = open(log_path).read()
            except:
                return AgentResult(task_id="", success=False, error=f"Cannot read {log_path}")
        # ponytail: grep errors, LLM for analysis
        error_lines = []
        for line in log_content.split("\n"):
            if any(kw in line.lower() for kw in ["error", "exception", "traceback", "critical", "fail"]):
                error_lines.append(line[:200])
        prompt = f"Analyze these log entries and identify the root problem:\n\n{log_content[:5000]}\n\nError lines found: {len(error_lines)}\nProvide diagnosis."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True,
            output={"llm_analysis": output, "error_lines": error_lines[:20], "total_errors": len(error_lines)},
            metadata={"error_count": len(error_lines), "log_truncated": len(error_lines) > 20}
        )

    async def _reproduce(self, data: Dict) -> AgentResult:
        prompt = f"Create a reproduction plan for:\nBug description: {data.get('description', '')}\nSteps: {data.get('steps', [])}\nEnvironment: {data.get('environment', {})}\nProvide step-by-step reproduction instructions."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True, output=output,
            metadata={"step_count": len(data.get("steps", []))}
        )

    async def _suggest_fix(self, data: Dict) -> AgentResult:
        prompt = f"Suggest a fix for:\nRoot cause: {data.get('root_cause', '')}\nApproach: {data.get('preferred_approach', 'minimal')}\nCode: {data.get('code', '')}\nProvide the fix with explanation."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True, output=output
        )
