from typing import Any, Dict
from backend.skills import BaseSkill, SkillResult, register
from backend.models.llm import LLMRequest


class CodeGenerationSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="code_generation",
            description="Generate implementation code from a specification using LLM + FileTool",
        )

    async def execute(self, context: Dict[str, Any], **kwargs) -> SkillResult:
        llm = context.get("llm")
        tools = context.get("tools", {})
        spec = kwargs.get("spec", kwargs.get("prompt", ""))
        language = kwargs.get("language", "python")
        output_path = kwargs.get("output_path", "")

        if not llm:
            return SkillResult(success=False, error="No LLM available in context")

        system = f"You are a {language} engineer. Generate production-quality code. Output ONLY the code, no explanations."
        req = LLMRequest(prompt=spec, system_prompt=system, max_tokens=4096, task_type="complex")
        resp = await llm.generate(req)

        if not resp.content:
            return SkillResult(success=False, error="LLM returned empty response")

        if output_path:
            file_tool = tools.get("file")
            if file_tool:
                await file_tool.execute(action="write", path=output_path, content=resp.content)

        return SkillResult(success=True, output=resp.content,
                           metadata={"language": language, "path": output_path,
                                     "tokens": resp.tokens_out, "model": resp.model})


class CodeReviewSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="code_review",
            description="Review source code files for bugs, security issues, and style problems",
        )

    REVIEW_PROMPT = """Review the following {language} code and identify:
1. **Bugs** — logic errors, runtime errors, edge cases
2. **Security** — injection, leaks, unsafe patterns
3. **Style** — readability, naming, consistency
4. **Performance** — bottlenecks, unnecessary work

For each finding: severity (critical/major/minor), location, description, fix suggestion.

Code to review:
```{language}
{code}
```"""

    async def execute(self, context: Dict[str, Any], **kwargs) -> SkillResult:
        llm = context.get("llm")
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        file_path = kwargs.get("file_path", "")

        if not code and file_path:
            tools = context.get("tools", {})
            file_tool = tools.get("file")
            if file_tool:
                result = await file_tool.execute(action="read", path=file_path)
                if result.success:
                    code = result.data

        if not code:
            return SkillResult(success=False, error="No code provided for review")
        if not llm:
            return SkillResult(success=False, error="No LLM available")

        prompt = self.REVIEW_PROMPT.format(language=language, code=code)
        req = LLMRequest(prompt=prompt, max_tokens=4096, task_type="complex")
        resp = await llm.generate(req)

        return SkillResult(success=True, output=resp.content,
                           metadata={"language": language, "file": file_path})


class TaskAnalysisSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="task_analysis",
            description="Analyze a task description and break it into concrete subtasks",
        )

    ANALYZE_PROMPT = """Analyze the following task and produce a structured breakdown.

Task: {task}

For each subtask provide:
- **name**: short name
- **description**: what to do
- **depends_on**: list of prerequisite subtask names (or "none")
- **estimated_effort**: small / medium / large
- **tools_needed**: tools that might be needed (file, command, web, git, database, docker)

Format as JSON list with keys: name, description, depends_on, estimated_effort, tools_needed"""

    async def execute(self, context: Dict[str, Any], **kwargs) -> SkillResult:
        llm = context.get("llm")
        task = kwargs.get("task", kwargs.get("description", ""))

        if not task:
            return SkillResult(success=False, error="No task description provided")
        if not llm:
            return SkillResult(success=False, error="No LLM available")

        prompt = self.ANALYZE_PROMPT.format(task=task)
        req = LLMRequest(prompt=prompt, max_tokens=4096, task_type="complex")
        resp = await llm.generate(req)

        return SkillResult(success=True, output=resp.content,
                           metadata={"model": resp.model, "tokens": resp.tokens_out})


register(CodeGenerationSkill())
register(CodeReviewSkill())
register(TaskAnalysisSkill())
