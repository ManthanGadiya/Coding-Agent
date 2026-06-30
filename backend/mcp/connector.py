from typing import Any, Dict, List, Optional
from contextlib import AsyncExitStack
from backend.mcp import (
    MCPServerConfig, TransportType, MCPResponse,
    _SERVER_REGISTRY, _CONNECTED_CLIENTS, log_use,
)


class MCPConnector:
    def __init__(self):
        self._stack = AsyncExitStack()
        self._session = None
        self._read = None
        self._write = None
        self._cleanup = None

    async def connect_stdio(self, config: MCPServerConfig) -> bool:
        from mcp.client.stdio import stdio_client
        import subprocess
        import shlex

        proc = await self._stack.enter_async_context(
            stdio_client(
                [config.command] + config.args,
                env=config.env or None,
            )
        )
        self._read, self._write = proc
        return await self._init_session(config.name)

    async def connect_sse(self, config: MCPServerConfig) -> bool:
        from mcp.client.sse import sse_client
        from httpx import URL

        stream = await self._stack.enter_async_context(
            sse_client(URL(config.url))
        )
        self._read, self._write = stream
        return await self._init_session(config.name)

    async def _init_session(self, name: str) -> bool:
        from mcp import ClientSession
        self._session = await self._stack.enter_async_context(
            ClientSession(self._read, self._write)
        )
        await self._session.initialize()
        _CONNECTED_CLIENTS[name] = self
        log_use({"event": "connect", "server": name})
        return True

    async def list_tools(self) -> List[Dict]:
        if not self._session:
            return []
        result = await self._session.list_tools()
        return [{"name": t.name, "description": t.description,
                 "inputSchema": t.inputSchema} for t in result.tools]

    async def call_tool(self, name: str, arguments: Dict = None) -> MCPResponse:
        if not self._session:
            return MCPResponse(success=False, error="Not connected")
        try:
            result = await self._session.call_tool(name, arguments or {})
            content = [c.text if hasattr(c, "text") else str(c) for c in result.content]
            return MCPResponse(success=not result.isError, data="\n".join(content),
                               metadata={"tool": name})
        except Exception as e:
            return MCPResponse(success=False, error=str(e))

    async def list_resources(self) -> List[Dict]:
        if not self._session:
            return []
        result = await self._session.list_resources()
        return [{"uri": r.uri, "name": r.name, "mimeType": r.mimeType} for r in result.resources]

    async def disconnect(self):
        await self._stack.aclose()
        for name, conn in list(_CONNECTED_CLIENTS.items()):
            if conn is self:
                del _CONNECTED_CLIENTS[name]
                log_use({"event": "disconnect", "server": name})


async def connect_server(name: str) -> bool:
    config = _SERVER_REGISTRY.get(name)
    if not config:
        return False
    if name in _CONNECTED_CLIENTS:
        return True
    conn = MCPConnector()
    if config.transport == TransportType.STDIO:
        return await conn.connect_stdio(config)
    return await conn.connect_sse(config)


async def disconnect_server(name: str):
    conn = _CONNECTED_CLIENTS.get(name)
    if conn:
        await conn.disconnect()


async def call_tool(server: str, tool: str, args: Dict = None) -> MCPResponse:
    conn = _CONNECTED_CLIENTS.get(server)
    if not conn:
        return MCPResponse(success=False, error=f"MCP server '{server}' not connected")
    result = await conn.call_tool(tool, args)
    log_use({"server": server, "tool": tool, "success": result.success})
    return result


async def get_tools(server: str) -> List[Dict]:
    conn = _CONNECTED_CLIENTS.get(server)
    if not conn:
        return []
    return await conn.list_tools()


async def get_all_tools() -> Dict[str, List[Dict]]:
    result = {}
    for name in list(_CONNECTED_CLIENTS.keys()):
        conn = _CONNECTED_CLIENTS[name]
        tools = await conn.list_tools()
        result[name] = tools
    return result
