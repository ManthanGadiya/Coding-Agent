import re
import subprocess
from pathlib import Path
from typing import Dict, Optional

from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage

SYSTEM_PROMPT = """You are an expert software engineer implementing code.
Given a specification, write clean, correct, maintainable code.
Output each file as a code block with the relative filepath in the opening fence:
```relative/path/to/file.py
<code>
```
Write all files needed for the implementation."""

# ponytail: dirs where overwriting an existing file is allowed (scratch/output)
_OVERWRITE_OK_DIRS = {"temp", "tmp", "output", "outputs", "build", "dist", "generated", "artifacts", "cache"}


class CoderAgent(BaseAgent):
    def __init__(self, agent_id: str = "coder-1", config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            name="Coder Agent",
            capabilities=[
                "implement", "refactor", "fix", "create_file",
                "modify_file", "run_build", "run_test", "run_lint"
            ],
            config=config
        )

    async def process_task(self, task: AgentTask) -> AgentResult:
        task_type = task.task_type
        data = task.input_data

        if task_type == "create_file":
            return await self._create_file(data)
        elif task_type == "modify_file":
            return await self._modify_file(data)
        elif task_type == "implement":
            return await self._implement(task)
        elif task_type == "refactor":
            return await self._refactor(data)
        elif task_type == "fix":
            return await self._fix(data)
        elif task_type == "run_build":
            return self._run_build(data)
        elif task_type == "run_test":
            return self._run_command("pytest", data)
        elif task_type == "run_lint":
            return self._run_command(data.get("lint_cmd", "ruff check"), data)
        else:
            return AgentResult(
                task_id=task.task_id,
                success=False,
                error=f"Unknown task type: {task_type}"
            )

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        if message.message_type == "query":
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=f"CoderAgent ready. Capabilities: {', '.join(self.capabilities)}",
                message_type="response"
            )
        return None

    async def _create_file(self, data: Dict) -> AgentResult:
        path = data.get("path")
        content = data.get("content", "")
        if not path:
            return AgentResult(task_id="", success=False, error="path required")
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content)
            return AgentResult(task_id="", success=True, output=f"Created {path}")
        except Exception as e:
            return AgentResult(task_id="", success=False, error=str(e))

    async def _modify_file(self, data: Dict) -> AgentResult:
        path = data.get("path")
        if not path or not Path(path).exists():
            return AgentResult(task_id="", success=False, error="path required and must exist")
        try:
            content = data.get("content")
            if content is not None:
                Path(path).write_text(content)
            return AgentResult(task_id="", success=True, output=f"Modified {path}")
        except Exception as e:
            return AgentResult(task_id="", success=False, error=str(e))

    async def _implement(self, task: AgentTask) -> AgentResult:
        base_path = task.input_data.get("base_path", str(Path.cwd()))
        spec = task.input_data.get("spec", task.description)
        prompt = f"Implement the following specification:\n\n{spec}\n\nUse relative paths from: {base_path}"
        output = await self._llm_generate(prompt, SYSTEM_PROMPT, max_tokens=4096)
        files_written = []
        errors = []
        base = Path(base_path).resolve()
        for match in re.finditer(r'```\r?\n?(.*?)```', output, re.DOTALL):
            block = match.group(1)
            first_line, _, content = block.partition("\n")
            filepath = first_line.strip()
            content = content.strip()
            # First line is a file path only if it looks like one (contains / \ or .);
            # otherwise (e.g. ```python) it's a language tag — skip the block.
            if not filepath or not any(c in filepath for c in "/\\."):
                continue
            full_path = (base / filepath).resolve()
            try:
                # ponytail: containment check — no escaping base_path via ../ or absolute paths
                if not full_path.is_relative_to(base):
                    errors.append(f"{filepath}: path escapes base directory")
                    continue
                # Never overwrite existing files outside scratch/output dirs
                if full_path.exists() and not any(
                    p.lower() in _OVERWRITE_OK_DIRS for p in full_path.parts
                ):
                    errors.append(f"{filepath}: would overwrite existing file")
                    continue
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                files_written.append(filepath)
            except Exception as e:
                errors.append(f"{filepath}: {e}")
        return AgentResult(
            task_id=task.task_id,
            success=len(files_written) > 0 and not errors,
            output=f"Wrote {len(files_written)} files: {', '.join(files_written)}" if files_written else output,
            error="; ".join(errors) if errors else None,
            metadata={"spec_snippet": spec[:200], "files_written": files_written, "task_type": "implementation"}
        )

    async def _refactor(self, data: Dict) -> AgentResult:
        path = data.get("path")
        if not path:
            return AgentResult(task_id="", success=False, error="path required")
        content = ""
        if Path(path).exists():
            content = Path(path).read_text()
        prompt = f"Refactor this code at {path}:\n\n{content}\n\nSuggest specific improvements."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True, output=output,
            metadata={"target": path}
        )

    async def _fix(self, data: Dict) -> AgentResult:
        path = data.get("path")
        issue = data.get("issue", "unknown")
        if not path:
            return AgentResult(task_id="", success=False, error="path required")
        content = ""
        if Path(path).exists():
            content = Path(path).read_text()
        prompt = f"Bug: {issue}\n\nCode at {path}:\n\n{content}\n\nDiagnose the issue and provide a fix."
        output = await self._llm_generate(prompt, SYSTEM_PROMPT)
        return AgentResult(
            task_id="", success=True, output=output,
            metadata={"target": path, "issue": issue}
        )

    def _run_build(self, data: Dict) -> AgentResult:
        cmd = data.get("build_cmd", "python -m build")
        return self._run_command(cmd, data)

    def _run_command(self, cmd: str, data: Dict) -> AgentResult:
        cwd = data.get("cwd", str(Path.cwd()))
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=300
            )
            return AgentResult(
                task_id="",
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                metadata={"returncode": result.returncode, "command": cmd}
            )
        except subprocess.TimeoutExpired:
            return AgentResult(task_id="", success=False, error="Command timed out")
        except Exception as e:
            return AgentResult(task_id="", success=False, error=str(e))
