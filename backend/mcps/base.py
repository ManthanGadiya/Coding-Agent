from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class MCPResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


class MCPClient:
    name: str = "base"
    base_url: str = ""

    async def call(self, tool: str, params: Optional[Dict] = None) -> MCPResult:
        raise NotImplementedError

    async def health(self) -> bool:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/health")
                return resp.status_code == 200
        except Exception:
            return False
