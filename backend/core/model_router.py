import httpx
import time
import json
from typing import Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass

from backend.config.settings import get_settings
from backend.models.llm import LLMRequest, LLMResponse

settings = get_settings()

MODEL_TIERS = {
    "local_small": ["qwen2.5-coder:1.5b", "llama3.2:1b"],
    "local_medium": ["qwen2.5-coder:7b", "llama3.1:8b", "mistral:7b"],
    "local_large": ["qwen2.5-coder:14b", "codellama:13b"],
    "cloud": ["gpt-4o", "claude-sonnet-4-20250514", "gemini-2.0-flash"],
}

TASK_MODEL_MAP = {
    "simple": "local_small",
    "moderate": "local_medium",
    "complex": "local_large",
    "critical": "cloud",
}


@dataclass
class ModelRoute:
    provider: str
    model: str
    endpoint: str
    api_key: Optional[str] = None


class ModelRouter:
    def __init__(self):
        self.routes: Dict[str, ModelRoute] = {}
        self._init_routes()

    def _init_routes(self):
        self.routes["ollama"] = ModelRoute(
            provider="ollama",
            model=settings.DEFAULT_LOCAL_MODEL,
            endpoint=f"{settings.OLLAMA_BASE_URL}/api/generate",
        )
        if settings.OPENAI_API_KEY:
            self.routes["openai"] = ModelRoute(
                provider="openai",
                model="gpt-4o",
                endpoint="https://api.openai.com/v1/chat/completions",
                api_key=settings.OPENAI_API_KEY,
            )
        if settings.ANTHROPIC_API_KEY:
            self.routes["anthropic"] = ModelRoute(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                endpoint="https://api.anthropic.com/v1/messages",
                api_key=settings.ANTHROPIC_API_KEY,
            )
        if settings.GEMINI_API_KEY:
            self.routes["gemini"] = ModelRoute(
                provider="gemini",
                model="gemini-2.0-flash",
                endpoint="https://generativelanguage.googleapis.com/v1beta/models",
                api_key=settings.GEMINI_API_KEY,
            )
        if settings.OPENAI_COMPATIBLE_BASE_URL and settings.OPENAI_COMPATIBLE_API_KEY:
            self.routes["openai-compatible"] = ModelRoute(
                provider="openai-compatible",
                model=settings.OPENAI_COMPATIBLE_MODEL,
                endpoint=settings.OPENAI_COMPATIBLE_BASE_URL.rstrip("/") + "/chat/completions",
                api_key=settings.OPENAI_COMPATIBLE_API_KEY,
            )

    def select_model(self, task_type: str = "general", complexity: str = "moderate") -> ModelRoute:
        tier = TASK_MODEL_MAP.get(complexity, "local_medium")
        if tier == "cloud":
            for name in ("openai", "anthropic", "gemini", "openai-compatible"):
                if name in self.routes:
                    return self.routes[name]
        return self.routes.get("ollama", list(self.routes.values())[0])

    async def generate(self, request: LLMRequest) -> LLMResponse:
        route = self.select_model(request.task_type, request.context.get("complexity", "moderate") if request.context else "moderate")
        start = time.time()

        if route.provider == "ollama":
            return await self._call_ollama(request, route, start)
        elif route.provider in ("openai", "openai-compatible"):
            return await self._call_openai(request, route, start)
        elif route.provider == "anthropic":
            return await self._call_anthropic(request, route, start)
        elif route.provider == "gemini":
            return await self._call_gemini(request, route, start)
        return LLMResponse(content="No model available", model="none", provider="none", latency_ms=0)

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        route = self.select_model(request.task_type, request.context.get("complexity", "moderate") if request.context else "moderate")

        if route.provider == "ollama":
            async for chunk in self._stream_ollama(request, route):
                yield chunk
        elif route.provider in ("openai", "openai-compatible"):
            async for chunk in self._stream_openai(request, route):
                yield chunk
        else:
            resp = await self.generate(request)
            yield resp.content

    def _build_messages(self, req: LLMRequest) -> list:
        msgs = []
        if req.system_prompt:
            msgs.append({"role": "system", "content": req.system_prompt})
        msgs.append({"role": "user", "content": req.prompt})
        return msgs

    async def _call_ollama(self, req: LLMRequest, route: ModelRoute, start: float) -> LLMResponse:
        payload = {
            "model": req.model or route.model,
            "prompt": req.prompt,
            "system": req.system_prompt or "",
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(route.endpoint, json=payload)
            data = resp.json()
        elapsed = (time.time() - start) * 1000
        return LLMResponse(
            content=data.get("response", ""),
            model=route.model, provider="ollama",
            tokens_in=data.get("prompt_eval_count", 0),
            tokens_out=data.get("eval_count", 0),
            latency_ms=elapsed,
        )

    async def _call_openai(self, req: LLMRequest, route: ModelRoute, start: float) -> LLMResponse:
        messages = self._build_messages(req)
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                route.endpoint,
                headers={"Authorization": f"Bearer {route.api_key}", "Content-Type": "application/json"},
                json={"model": route.model, "messages": messages, "temperature": req.temperature, "max_tokens": req.max_tokens},
            )
            data = resp.json()
        elapsed = (time.time() - start) * 1000
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=route.model, provider=route.provider,
            tokens_in=data.get("usage", {}).get("prompt_tokens", 0),
            tokens_out=data.get("usage", {}).get("completion_tokens", 0),
            latency_ms=elapsed,
        )

    async def _call_anthropic(self, req: LLMRequest, route: ModelRoute, start: float) -> LLMResponse:
        messages = [{"role": "user", "content": req.prompt}]
        headers = {"x-api-key": route.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        payload = {"model": route.model, "messages": messages, "max_tokens": req.max_tokens, "temperature": req.temperature}
        if req.system_prompt:
            payload["system"] = req.system_prompt
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(route.endpoint, headers=headers, json=payload)
            data = resp.json()
        elapsed = (time.time() - start) * 1000
        return LLMResponse(
            content=data["content"][0]["text"],
            model=route.model, provider="anthropic",
            tokens_in=data.get("usage", {}).get("input_tokens", 0),
            tokens_out=data.get("usage", {}).get("output_tokens", 0),
            latency_ms=elapsed,
        )

    async def _call_gemini(self, req: LLMRequest, route: ModelRoute, start: float) -> LLMResponse:
        contents = [{"parts": [{"text": req.prompt}]}]
        payload = {"contents": contents, "generationConfig": {"temperature": req.temperature, "maxOutputTokens": req.max_tokens}}
        if req.system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": req.system_prompt}]}
        url = f"{route.endpoint}/{route.model}:generateContent?key={route.api_key}"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload)
            data = resp.json()
        elapsed = (time.time() - start) * 1000
        text = ""
        candidates = data.get("candidates", [])
        if candidates:
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return LLMResponse(
            content=text, model=route.model, provider="gemini",
            latency_ms=elapsed,
        )

    async def _stream_ollama(self, req: LLMRequest, route: ModelRoute) -> AsyncGenerator[str, None]:
        payload = {
            "model": req.model or route.model,
            "prompt": req.prompt,
            "system": req.system_prompt or "",
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", route.endpoint, json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            pass

    async def _stream_openai(self, req: LLMRequest, route: ModelRoute) -> AsyncGenerator[str, None]:
        messages = self._build_messages(req)
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST", route.endpoint,
                headers={"Authorization": f"Bearer {route.api_key}", "Content-Type": "application/json"},
                json={"model": route.model, "messages": messages, "temperature": req.temperature, "max_tokens": req.max_tokens, "stream": True},
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            pass


_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
