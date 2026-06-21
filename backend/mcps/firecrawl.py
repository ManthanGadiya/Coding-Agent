import httpx
from typing import Optional, Dict, Any

from backend.mcps.base import MCPClient, MCPResult
from backend.config.settings import get_settings

settings = get_settings()


class FirecrawlMCP(MCPClient):
    name = "firecrawl"
    base_url = settings.FIRECRAWL_MCP_URL

    async def call(self, tool: str, params: Optional[Dict] = None) -> MCPResult:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(f"{self.base_url}/call", json={"tool": tool, "params": params or {}})
                data = resp.json()
                return MCPResult(success=resp.status_code == 200, data=data.get("result"), raw=data)
        except Exception as e:
            return MCPResult(success=False, error=str(e))

    async def scrape(self, url: str) -> MCPResult:
        return await self.call("scrape", {"url": url})

    async def search(self, query: str, count: int = 5) -> MCPResult:
        return await self.call("search", {"query": query, "count": count})

    async def crawl(self, url: str, max_pages: int = 10) -> MCPResult:
        return await self.call("crawl", {"url": url, "max_pages": max_pages})
