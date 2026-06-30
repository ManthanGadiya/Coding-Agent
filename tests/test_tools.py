import pytest
from backend.tools import (
    TOOL_REGISTRY, ToolChain, run_parallel, mode_allows_tool,
    ToolRiskLevel, _validate_command, _validate_path, PROJECT_ROOT,
)


def test_registry_has_six_tools():
    assert set(TOOL_REGISTRY.keys()) == {"file", "command", "web", "git", "database", "docker"}


@pytest.mark.parametrize("name,expected_risk", [
    ("file", "medium"), ("command", "high"), ("web", "low"),
    ("git", "medium"), ("database", "high"), ("docker", "high"),
])
def test_tool_risk_levels(name, expected_risk):
    assert TOOL_REGISTRY[name].risk_level.value == expected_risk


def test_command_sandbox_blocks_disallowed():
    cmd = TOOL_REGISTRY["command"]
    assert _validate_command("rm -rf /") is not None
    assert _validate_command("sudo rm -rf") is not None
    assert _validate_command("") is not None
    assert _validate_command("ls -la") is None


def test_path_jail_blocks_outside():
    outside = "C:\\Windows\\System32"
    err = _validate_path(outside)
    assert err is not None
    assert "outside project root" in err

    inside = str(PROJECT_ROOT)
    assert _validate_path(inside) is None


@pytest.mark.parametrize("mode,risk,allowed", [
    ("teaching", "low", True), ("teaching", "medium", True),
    ("teaching", "high", False), ("teaching", "critical", False),
    ("build", "high", True), ("build", "critical", False),
    ("autonomous", "critical", True),
])
def test_mode_gating(mode, risk, allowed):
    assert mode_allows_tool(mode, ToolRiskLevel(risk)) == allowed


@pytest.mark.asyncio
async def test_file_tool_read_write():
    ft = TOOL_REGISTRY["file"]
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        tmp = f.name
    try:
        r = await ft.execute(action="read", path=tmp)
        assert r.success
        assert r.data == "hello world"
    finally:
        os.unlink(tmp)


@pytest.mark.asyncio
async def test_file_tool_write():
    ft = TOOL_REGISTRY["file"]
    import tempfile, os
    tmp = tempfile.mktemp(suffix=".txt")
    try:
        r = await ft.execute(action="write", path=tmp, content="test content")
        assert r.success
        with open(tmp) as f:
            assert f.read() == "test content"
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@pytest.mark.asyncio
async def test_tool_chain_empty():
    chain = ToolChain([])
    results = await chain.run()
    assert results == []


@pytest.mark.asyncio
async def test_tool_chain_invalid_tool():
    chain = ToolChain([{"tool": "nonexistent", "params": {}}])
    results = await chain.run()
    assert len(results) == 1
    assert not results[0].success
    assert "not found" in results[0].error


@pytest.mark.asyncio
async def test_file_tool_search():
    ft = TOOL_REGISTRY["file"]
    r = await ft.execute(action="search", path=str(PROJECT_ROOT), pattern="import pytest", max_results=3)
    assert r.success
    assert isinstance(r.data, list)


@pytest.mark.asyncio
async def test_command_list():
    ct = TOOL_REGISTRY["command"]
    r = await ct.execute(command="ls -la", cwd=str(PROJECT_ROOT))
    assert r.success
