from backend.mcps.base import MCPClient, MCPResult
from backend.mcps.firecrawl import FirecrawlMCP
from backend.mcps.github import GitHubMCP
from backend.mcps.agent_memory import AgentMemoryMCP
from backend.mcps.markitdown import MarkItDownMCP

MCP_REGISTRY = {
    "firecrawl": FirecrawlMCP,
    "github": GitHubMCP,
    "agent_memory": AgentMemoryMCP,
    "markitdown": MarkItDownMCP,
}


def get_mcp(name: str) -> MCPClient:
    cls = MCP_REGISTRY.get(name)
    if not cls:
        raise ValueError(f"MCP not found: {name}. Available: {list(MCP_REGISTRY.keys())}")
    return cls()
