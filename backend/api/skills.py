from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.skills import get, list_skills, get_log
from backend.skills.builtin import CodeGenerationSkill, CodeReviewSkill, TaskAnalysisSkill
from backend.core.model_router import get_model_router
from backend.tools import TOOL_REGISTRY

router = APIRouter(tags=["skills"])


class SkillExecuteRequest(BaseModel):
    name: str
    params: dict = {}
    agent_id: str = ""
    session_id: str = ""


@router.post("/execute")
async def execute_skill(req: SkillExecuteRequest):
    skill = get(req.name)
    if not skill:
        raise HTTPException(404, f"Skill '{req.name}' not found")

    context = {
        "llm": get_model_router(),
        "tools": TOOL_REGISTRY,
        "agent_id": req.agent_id,
        "session_id": req.session_id,
    }
    result = await skill.execute(context, **req.params)
    return {"success": result.success, "output": result.output,
            "error": result.error, "metadata": result.metadata}


@router.get("/list")
async def list_all_skills():
    return {"skills": list_skills()}


@router.get("/log")
async def skill_log(limit: int = 50):
    return {"entries": get_log(limit)}
