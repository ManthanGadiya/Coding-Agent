import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage

SYSTEM_PROMPT = """You are a senior QA engineer. Write thorough tests
covering edge cases, error states, and normal flows.
Output only test code and a brief explanation of coverage."""


class TesterAgent(BaseAgent):
    def __init__(self, agent_id: str = "tester-1", config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            name="Tester Agent",
            capabilities=[
                "write_test", "run_test", "run_test_suite",
                "check_coverage", "validate_behavior"
            ],
            config=config
        )

    async def process_task(self, task: AgentTask) -> AgentResult:
        task_type = task.task_type
        data = task.input_data

        if task_type == "write_test":
            return await self._write_test(data)
        elif task_type == "run_test":
            return self._run_test(data)
        elif task_type == "run_test_suite":
            return self._run_suite(data)
        elif task_type == "check_coverage":
            return self._check_coverage(data)
        elif task_type == "validate_behavior":
            return self._validate(data)
        else:
            return AgentResult(
                task_id=task.task_id,
                success=False,
                error=f"Unknown test type: {task_type}"
            )

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        if message.message_type == "query":
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=f"TesterAgent ready. Capabilities: {', '.join(self.capabilities)}",
                message_type="response"
            )
        return None

    async def _write_test(self, data: Dict) -> AgentResult:
        target = data.get("target", "")
        framework = data.get("framework", "pytest")
        path = data.get("path", f"tests/test_{Path(target).stem}.py")
        source_content = data.get("source", "")
        if not source_content and target:
            try:
                source_content = Path(target).read_text()
            except:
                pass
        prompt = f"Write {framework} tests for:\n\n{source_content}\n\nCover normal cases, edge cases, and error conditions. Output only the test code."
        content = await self._llm_generate(prompt, SYSTEM_PROMPT, max_tokens=2048)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content)
        return AgentResult(
            task_id="", success=True,
            output=f"Tests written to {path}\n\n{content}",
            metadata={"framework": framework, "path": path}
        )

    def _run_test(self, data: Dict) -> AgentResult:
        path = data.get("path", ".")
        cmd = data.get("cmd", f"pytest {path} -v")
        return self._run_cmd(cmd, data)

    def _run_suite(self, data: Dict) -> AgentResult:
        cmd = data.get("cmd", "pytest -v")
        return self._run_cmd(cmd, data)

    def _check_coverage(self, data: Dict) -> AgentResult:
        cmd = data.get("cmd", "pytest --cov --cov-report=term-missing")
        return self._run_cmd(cmd, data)

    def _validate(self, data: Dict) -> AgentResult:
        input_data = data.get("input")
        expected = data.get("expected")
        actual = data.get("actual")
        passed = expected == actual
        return AgentResult(
            task_id="", success=passed,
            output={"passed": passed, "expected": expected, "actual": actual},
            metadata={"validation_type": data.get("type", "equality")}
        )

    def _run_cmd(self, cmd: str, data: Dict) -> AgentResult:
        cwd = data.get("cwd", str(Path.cwd()))
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=600
            )
            return AgentResult(
                task_id="",
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                metadata={"returncode": result.returncode, "command": cmd}
            )
        except subprocess.TimeoutExpired:
            return AgentResult(task_id="", success=False, error="Test timed out")
        except Exception as e:
            return AgentResult(task_id="", success=False, error=str(e))
