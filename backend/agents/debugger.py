from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage


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
            return self._diagnose(data)
        elif task_type == "analyze_error":
            return self._analyze_error(data)
        elif task_type == "trace":
            return self._trace(data)
        elif task_type == "check_logs":
            return self._check_logs(data)
        elif task_type == "reproduce":
            return self._reproduce(data)
        elif task_type == "suggest_fix":
            return self._suggest_fix(data)
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

    def _diagnose(self, data: Dict) -> AgentResult:
        error = data.get("error", "")
        context = data.get("context", "")
        code_snippet = data.get("code_snippet", "")

        hypotheses = []
        if error:
            if "KeyError" in error:
                hypotheses.append({"cause": "Missing key in dict", "severity": "high", "check": "Verify key exists before access"})
            if "AttributeError" in error:
                hypotheses.append({"cause": "Wrong type or None access", "severity": "high", "check": "Check object type and None handling"})
            if "TypeError" in error:
                hypotheses.append({"cause": "Type mismatch or wrong arg count", "severity": "high", "check": "Verify argument types and signatures"})
            if "ImportError" in error or "ModuleNotFoundError" in error:
                hypotheses.append({"cause": "Missing dependency or wrong import path", "severity": "high", "check": "Install package or fix import path"})
            if "IndexError" in error:
                hypotheses.append({"cause": "List/tuple index out of range", "severity": "high", "check": "Verify list bounds before access"})

        # ponytail: pattern-matching on error strings, LLM diagnostics when more depth needed
        return AgentResult(
            task_id="",
            success=True,
            output={
                "hypotheses": hypotheses,
                "suggested_actions": [h["check"] for h in hypotheses],
                "needs_llm": len(hypotheses) == 0
            },
            metadata={"hypothesis_count": len(hypotheses), "error_type": error.split(":")[0] if ":" in error else "unknown"}
        )

    def _analyze_error(self, data: Dict) -> AgentResult:
        traceback = data.get("traceback", "")
        lines = traceback.split("\n") if traceback else []

        frames = []
        for line in lines:
            if 'File "' in line:
                parts = line.strip().split(", ")
                for p in parts:
                    if p.startswith('File "'):
                        frames.append(p.replace('File "', "").replace('"', ""))

        return AgentResult(
            task_id="",
            success=True,
            output={
                "traceback_frames": frames,
                "last_frame": frames[-1] if frames else "unknown",
                "line_count": len(lines)
            },
            metadata={"frame_count": len(frames)}
        )

    def _trace(self, data: Dict) -> AgentResult:
        path = data.get("path", "")
        function = data.get("function", "")

        return AgentResult(
            task_id="",
            success=True,
            output=f"Trace analysis for {path}:{function if function else 'all'}",
            metadata={"path": path, "function": function}
        )

    def _check_logs(self, data: Dict) -> AgentResult:
        log_content = data.get("content", "")
        log_path = data.get("path")

        if not log_content and log_path:
            try:
                log_content = open(log_path).read()
            except:
                return AgentResult(task_id="", success=False, error=f"Cannot read {log_path}")

        error_lines = []
        for line in log_content.split("\n"):
            if any(kw in line.lower() for kw in ["error", "exception", "traceback", "critical", "fail"]):
                error_lines.append(line[:200])

        # ponytail: grep errors from logs, structured parsing when patterns known
        return AgentResult(
            task_id="",
            success=True,
            output={"error_lines": error_lines[:20], "total_errors": len(error_lines)},
            metadata={"error_count": len(error_lines), "log_truncated": len(error_lines) > 20}
        )

    def _reproduce(self, data: Dict) -> AgentResult:
        steps = data.get("steps", [])
        environment = data.get("environment", {})

        return AgentResult(
            task_id="",
            success=True,
            output=f"Reproduction plan with {len(steps)} steps",
            metadata={"step_count": len(steps), "environment": environment}
        )

    def _suggest_fix(self, data: Dict) -> AgentResult:
        root_cause = data.get("root_cause", "")
        approach = data.get("preferred_approach", "minimal")

        return AgentResult(
            task_id="",
            success=True,
            output={
                "root_cause": root_cause,
                "suggestion": f"Fix {root_cause}" if root_cause else "See diagnosis results",
                "approach": approach
            }
        )