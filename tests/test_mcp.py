import pytest
from backend.mcp import (
    MCPServerConfig, TransportType, MCPResponse,
    register_server, remove_server, get_server, list_servers,
    list_connected, log_use, get_log,
)


def test_register_and_list():
    register_server(MCPServerConfig(name="test-srv", transport=TransportType.STDIO, command="echo"))
    assert len(list_servers()) >= 1
    names = [s["name"] for s in list_servers()]
    assert "test-srv" in names
    remove_server("test-srv")
    assert "test-srv" not in [s["name"] for s in list_servers()]


def test_get_server():
    register_server(MCPServerConfig(name="get-test", transport=TransportType.SSE, url="http://localhost:9999"))
    srv = get_server("get-test")
    assert srv is not None
    assert srv.url == "http://localhost:9999"
    assert srv.transport == TransportType.SSE
    remove_server("get-test")


def test_log():
    log_use({"event": "test", "server": "test"})
    entries = get_log()
    assert len(entries) >= 1
    assert entries[-1]["event"] == "test"
    assert "timestamp" in entries[-1]


@pytest.mark.asyncio
async def test_connect_nonexistent():
    from backend.mcp.connector import connect_server
    ok = await connect_server("this-does-not-exist")
    assert not ok


@pytest.mark.asyncio
async def test_call_tool_not_connected():
    from backend.mcp.connector import call_tool
    result = await call_tool("nonexistent", "some-tool")
    assert not result.success
    assert "not connected" in result.error
