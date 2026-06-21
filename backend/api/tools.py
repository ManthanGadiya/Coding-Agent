from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

from backend.tools import (
    TOOL_REGISTRY, get_tool, get_tool_audit_log, ToolResult
)
from backend.core.autonomy import AutonomyController, SafetyManager
from backend.core.safety import safety_controller

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


class SafetyImpactRequest(BaseModel):
    action: str
    target: str


@router.post("/safety/impact")
async def impact_report(req: SafetyImpactRequest):
    report = safety.impact_report(req.action, req.target)
    return report


@router.get("/safety/backups")
async def backup_history(limit: int = 20):
    return {"backups": safety.get_backup_history(limit)}


class ScanSecretsRequest(BaseModel):
    content: str
    filename: str = ""


@router.post("/safety/scan-secrets")
async def scan_secrets(req: ScanSecretsRequest):
    return safety_controller.scan_secrets(req.content, req.filename)


class ScanFileSecretsRequest(BaseModel):
    path: str


@router.post("/safety/scan-file-secrets")
async def scan_file_secrets(req: ScanFileSecretsRequest):
    return safety_controller.scan_file_secrets(req.path)


class VerifyBackupRequest(BaseModel):
    backup_path: str


@router.post("/safety/verify-backup")
async def verify_backup(req: VerifyBackupRequest):
    return safety_controller.verify_backup(req.backup_path)


@router.post("/safety/pre-check")
async def pre_operation_check(action: str, target: str, content: str = ""):
    return safety_controller.check_pre_operation(action, target, content)
