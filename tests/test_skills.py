import pytest
from backend.skills import register, get, list_skills, get_log, BaseSkill, SkillResult


class DummySkill(BaseSkill):
    def __init__(self):
        super().__init__(name="dummy", description="test skill")
    async def execute(self, context, **kwargs):
        return SkillResult(success=True, output=f"hello {kwargs.get('name', 'world')}")


def setup_module():
    register(DummySkill())


def test_register_and_list():
    skills = list_skills()
    names = [s["name"] for s in skills]
    assert "dummy" in names
    assert "code_generation" in names
    assert "code_review" in names
    assert "task_analysis" in names


def test_get_skill():
    s = get("dummy")
    assert s is not None
    assert s.name == "dummy"
    assert s.description == "test skill"


def test_get_nonexistent():
    assert get("nope") is None


@pytest.mark.asyncio
async def test_execute_dummy():
    s = get("dummy")
    result = await s.execute({}, name="test")
    assert result.success
    assert result.output == "hello test"


@pytest.mark.asyncio
async def test_code_generation_no_llm():
    s = get("code_generation")
    result = await s.execute({}, spec="print hello")
    assert not result.success
    assert "No LLM" in result.error


@pytest.mark.asyncio
async def test_code_review_no_code():
    s = get("code_review")
    result = await s.execute({})
    assert not result.success
    assert "No code" in result.error


@pytest.mark.asyncio
async def test_task_analysis_no_task():
    s = get("task_analysis")
    result = await s.execute({})
    assert not result.success
    assert "No task" in result.error


def test_log():
    entries = get_log()
    assert isinstance(entries, list)
