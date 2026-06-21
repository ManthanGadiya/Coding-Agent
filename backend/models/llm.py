from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class LLMRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    task_type: str = "general"
    context: Optional[Dict[str, Any]] = None


class LLMResponse(BaseModel):
    content: str
    model: str
    provider: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    confidence: float = 1.0
