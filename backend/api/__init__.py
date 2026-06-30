from fastapi import APIRouter

from backend.api.tasks import router as tasks_router
from backend.api.agents import router as agents_router
from backend.api.memory import router as memory_router
from backend.api.workflows import router as workflows_router
from backend.api.projects import router as projects_router
from backend.api.llm import router as llm_router
from backend.api.decisions import router as decisions_router
from backend.api.autonomy import router as autonomy_router
from backend.api.learning import router as learning_router
from backend.api.memory_retrieval import router as memory_retrieval_router
from backend.api.tools import router as tools_router
from backend.api.user import router as user_router
from backend.api.mcp import router as mcp_router

router = APIRouter()

router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
router.include_router(agents_router, prefix="/agents", tags=["agents"])
router.include_router(memory_router, prefix="/memory", tags=["memory"])
router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
router.include_router(projects_router, prefix="/projects", tags=["projects"])
router.include_router(llm_router, prefix="/llm", tags=["llm"])
router.include_router(decisions_router, prefix="/decisions", tags=["decisions"])
router.include_router(autonomy_router, prefix="/autonomy", tags=["autonomy"])
router.include_router(learning_router, prefix="/learning", tags=["learning"])
router.include_router(memory_retrieval_router, prefix="/memory-retrieval", tags=["memory-retrieval"])
router.include_router(tools_router, prefix="/tools", tags=["tools"])
router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(mcp_router, prefix="/mcp", tags=["mcp"])