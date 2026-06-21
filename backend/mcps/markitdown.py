from backend.mcp.base import MCPClient, MCPResult
from typing import Optional, Dict


class MarkItDownMCP(MCPClient):
    name = "markitdown"
    base_url = ""  # uses local markitdown library

    async def call(self, tool: str, params: Optional[Dict] = None) -> MCPResult:
        return MCPResult(success=False, error="Use markitdown directly. MCP server not implemented.")

    async def convert_file(self, path: str) -> MCPResult:
        try:
            import subprocess
            result = subprocess.run(
                ["markitdown", path],
                capture_output=True, text=True, timeout=30
            )
            return MCPResult(success=result.returncode == 0, data=result.stdout)
        except Exception as e:
            return MCPResult(success=False, error=str(e))
