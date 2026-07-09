from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from pydantic import BaseModel
from backend.core.memory_retrieval import MemoryRetriever

router = APIRouter()
retriever = MemoryRetriever()


class MemoryAdd(BaseModel):
    content: str
    tags: List[str] = []
    importance: float = 0.5
    confidence: float = 0.7
    outcome_quality: float = 0.5
    relationships: List[str] = []
    agent: str = ""


class RetrieveRequest(BaseModel):
    query: str
    agent: str = ""
    mode: str = ""
    context_tags: List[str] = []
    task_complexity: str = "moderate"
    weights: Optional[Dict[str, float]] = None
    top_n: Optional[int] = None


@router.post("/store")
def store_memory(req: MemoryAdd):
    return retriever.add_memory(
        content=req.content, tags=req.tags,
        importance=req.importance, confidence=req.confidence,
        outcome_quality=req.outcome_quality,
        relationships=req.relationships, agent=req.agent,
    )


@router.post("/retrieve")
def retrieve_memories(req: RetrieveRequest):
    return retriever.retrieve(
        query=req.query, agent=req.agent, mode=req.mode,
        context_tags=req.context_tags,
        task_complexity=req.task_complexity,
        weights=req.weights, top_n=req.top_n,
    )


@router.post("/expand")
def expand_relationships(req: RetrieveRequest):
    return retriever.expand_relationships(
        query=req.query, agent=req.agent, mode=req.mode,
        context_tags=req.context_tags,
        task_complexity=req.task_complexity,
    )


@router.get("/profile/{agent}")
def get_profile(agent: str):
    return retriever.get_profile(agent)


@router.get("/profiles")
def list_profiles():
    from backend.core.memory_retrieval import AGENT_RETRIEVAL_PROFILES
    return AGENT_RETRIEVAL_PROFILES
