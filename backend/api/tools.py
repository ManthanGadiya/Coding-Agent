from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

from backend.tools import (
    TOOL_REGISTRY, get_tool, get_tool_audit_log, ToolResult
)
from backend.core.autonomy import AutonomyController, SafetyManager

router = APIRouter(prefix="/tools", tags=["tools"])

autonomy = AutonomyController()
safety = SafetyManager()


class ToolExecuteRequest(BaseModel):
    tool: str
    action: str = "execute"
    params: dict = {}
    agent_id: str = ""
    agent_role: str = ""
    session_id: str = ""


@router.post("/execute")
async def execute_tool(req: ToolExecuteRequest):
    tool = get_tool(req.tool)
    if not tool:
        raise HTTPException(404, f"Tool '{req.tool}' not found")

    tool.set_autonomy_check(
        lambda cap, role, sid: autonomy.can_execute(cap, role, sid).__getitem__("can_execute")
        if hasattr(autonomy.can_execute(cap, role, sid), "__getitem__")
        else autonomy.can_execute(cap, role, sid)
    )

    result = await tool.safe_execute(
        agent_id=req.agent_id, agent_role=req.agent_role,
        session_id=req.session_id, **req.params
    )
    return {"success": result.success, "data": result.data,
            "error": result.error, "warnings": result.warnings,
            "metadata": result.metadata}


@router.get("/list")
async def list_tools():
    return {
        "tools": [{"name": t.name, "description": t.description,
                    "risk_level": t.risk_level.value,
                    "capabilities": t.required_capabilities}
                  for t in TOOL_REGISTRY.values()]
    }


@router.get("/audit")
async def tool_audit(limit: int = 50):
    return {"entries": get_tool_audit_log(limit)}


class SafetyBackupRequest(BaseModel):
    path: str


@router.post("/safety/backup")
async def create_backup(req: SafetyBackupRequest):
    record = safety.backup(req.path)
    return {"backup_path": record.backup_path, "timestamp": record.timestamp, "size": record.size}


@router.post("/safety/rollback")
async def rollback_backup(path: str):
    for rec in reversed(safety.backups):
        if rec.path == path:
            ok = safety.rollback(rec)
            return {"success": ok, "path": path, "backup": rec.backup_path}
    raise HTTPException(404, f"No backup found for {path}")


class ImpactRequest(BaseModel):
    action: str
    target: str


@router.post("/safety/impact")
async def impact_report(req: ImpactRequest):
    report = safety.impact_report(req.action, req.target)
    return report


@router.get("/safety/backups")
async def backup_history(limit: int = 20):
    return {"backups": safety.get_backup_history(limit)}
