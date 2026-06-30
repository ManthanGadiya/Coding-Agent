from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.mcp import (
    MCPServerConfig, TransportType, MCPResponse,
    register_server, remove_server, get_server, list_servers,
    list_connected, get_log,
)
from backend.mcp.connector import connect_server, disconnect_server, call_tool, get_tools, get_all_tools

router = APIRouter(tags=["mcp"])


class AddServerRequest(BaseModel):
    name: str
    transport: str = "stdio"
    command: str = ""
    args: list = []
    url: str = ""
    env: dict = {}


@router.post("/servers")
async def add_server(req: AddServerRequest):
    if get_server(req.name):
        raise HTTPException(400, f"Server '{req.name}' already registered")
    transport = TransportType.STDIO if req.transport == "stdio" else TransportType.SSE
    config = MCPServerConfig(name=req.name, transport=transport, command=req.command,
                              args=req.args, url=req.url, env=req.env)
    register_server(config)
    return {"name": req.name, "transport": req.transport}


@router.delete("/servers/{name}")
async def delete_server(name: str):
    await disconnect_server(name)
    remove_server(name)
    return {"name": name, "deleted": True}


@router.get("/servers")
async def list_all_servers():
    return {"servers": list_servers(), "connected": list_connected()}


@router.post("/servers/{name}/connect")
async def connect(name: str):
    ok = await connect_server(name)
    if not ok:
        raise HTTPException(404, f"Server '{name}' not found or connection failed")
    return {"name": name, "connected": True}


@router.post("/servers/{name}/disconnect")
async def disconnect(name: str):
    await disconnect_server(name)
    return {"name": name, "disconnected": True}


@router.get("/servers/{name}/tools")
async def list_tools(name: str):
    tools = await get_tools(name)
    return {"server": name, "tools": tools}


@router.get("/tools")
async def list_all_connected_tools():
    tools = await get_all_tools()
    return {"tools": tools}


class CallToolRequest(BaseModel):
    server: str
    tool: str
    arguments: dict = {}


@router.post("/call")
async def call_mcp_tool(req: CallToolRequest):
    result = await call_tool(req.server, req.tool, req.arguments)
    return {"success": result.success, "data": result.data,
            "error": result.error, "metadata": result.metadata}


@router.get("/log")
async def mcp_log(limit: int = 50):
    return {"entries": get_log(limit)}
