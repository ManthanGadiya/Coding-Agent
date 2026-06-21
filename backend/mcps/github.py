import httpx
from typing import Optional, Dict, Any

from backend.mcp.base import MCPClient, MCPResult
from backend.config.settings import get_settings

settings = get_settings()


class GitHubMCP(MCPClient):
    name = "github"
    base_url = settings.GITHUB_MCP_URL

    def __init__(self):
        super().__init__()
        self.api_base = "https://api.github.com"
        self.token = settings.GITHUB_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github.v3+json"} if self.token else {}

    async def call(self, tool: str, params: Optional[Dict] = None) -> MCPResult:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(f"{self.base_url}/call", json={"tool": tool, "params": params or {}})
                data = resp.json()
                return MCPResult(success=resp.status_code == 200, data=data.get("result"), raw=data)
        except Exception as e:
            return MCPResult(success=False, error=str(e))

    async def get_file(self, owner: str, repo: str, path: str, branch: str = "main") -> MCPResult:
        return await self.call("get_file", {"owner": owner, "repo": repo, "path": path, "branch": branch})

    async def search_code(self, query: str) -> MCPResult:
        url = f"{self.api_base}/search/code?q={query}"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers=self.headers)
                data = resp.json()
                return MCPResult(success=resp.status_code == 200, data=data.get("items", []))
        except Exception as e:
            return MCPResult(success=False, error=str(e))
