import httpx
from typing import Optional, Dict, Any

from backend.mcp.base import MCPClient, MCPResult
from backend.config.settings import get_settings

settings = get_settings()


class AgentMemoryMCP(MCPClient):
    name = "agent_memory"
    base_url = settings.AGENT_MEMORY_MCP_URL

    async def call(self, tool: str, params: Optional[Dict] = None) -> MCPResult:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(f"{self.base_url}/call", json={"tool": tool, "params": params or {}})
                data = resp.json()
                return MCPResult(success=resp.status_code == 200, data=data.get("result"), raw=data)
        except Exception as e:
            return MCPResult(success=False, error=str(e))

    async def save(self, key: str, value: Any, category: str = "general", tags: Optional[list] = None) -> MCPResult:
        return await self.call("save", {"key": key, "value": value, "category": category, "tags": tags})

    async def retrieve(self, key: str) -> MCPResult:
        return await self.call("retrieve", {"key": key})

    async def search(self, query: str, limit: int = 10) -> MCPResult:
        return await self.call("search", {"query": query, "limit": limit})
