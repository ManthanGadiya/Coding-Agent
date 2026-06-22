from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.models.llm import LLMRequest, LLMResponse
from backend.core.model_router import get_model_router

router = APIRouter()


@router.post("/generate", response_model=LLMResponse)
async def generate(request: LLMRequest):
    router = get_model_router()
    try:
        return await router.generate(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
def list_models():
    router = get_model_router()
    return {"routes": list(router.routes.keys())}


@router.post("/select")
def select_model(data: dict):
    router = get_model_router()
    route = router.select_model(data.get("task_type", "general"), data.get("complexity", "moderate"))
    return {"provider": route.provider, "model": route.model}


@router.post("/stream")
async def generate_stream(request: LLMRequest):
    router = get_model_router()
    return StreamingResponse(router.generate_stream(request), media_type="text/event-stream")
