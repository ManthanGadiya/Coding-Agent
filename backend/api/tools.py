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
    mode: str = "build"


@router.post("/execute")
async def execute_tool(req: ToolExecuteRequest):
    tool = get_tool(req.tool)
    if not tool:
        raise HTTPException(404, f"Tool '{req.tool}' not found")

    result = await tool.safe_execute(
        agent_id=req.agent_id, agent_role=req.agent_role,
        session_id=req.session_id, mode=req.mode, **req.params
    )
    return {"success": result.success, "data": result.data,
            "error": result.error, "warnings": result.warnings,
            "metadata": result.metadata}


class ChainExecuteRequest(BaseModel):
    steps: list = []
    initial: dict = {}
    mode: str = "build"


@router.post("/chain")
async def execute_chain(req: ChainExecuteRequest):
    from backend.tools import ToolChain
    chain = ToolChain(req.steps, mode=req.mode)
    results = await chain.run(req.initial)
    return {"results": [{"success": r.success, "data": r.data,
                          "error": r.error} for r in results]}


class ParallelExecuteRequest(BaseModel):
    tool: str
    items: list = []
    mode: str = "build"


@router.post("/parallel")
async def execute_parallel(req: ParallelExecuteRequest):
    from backend.tools import run_parallel
    results = await run_parallel(req.tool, req.items, mode=req.mode)
    return {"results": [{"success": r.success, "data": r.data,
                          "error": r.error} for r in results]}


@router.get("/list")
async def list_tools():
    return {
        "tools": [{"name": t.name, "description": t.description,
                    "risk_level": t.risk_level.value,
                    "permissions": [p.value for p in t.required_permissions]}
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
