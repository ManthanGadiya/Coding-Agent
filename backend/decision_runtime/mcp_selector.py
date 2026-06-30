from typing import Any, Dict, List, Optional, Set

from backend.decision_runtime.registries import mcp_registry, MCPDef
from backend.decision_runtime.task_classifier import TaskType, ClassificationResult


MCP_TASK_MAP: Dict[TaskType, List[str]] = {
    TaskType.RESEARCH: ["firecrawl", "markitdown"],
    TaskType.LEARNING: ["firecrawl"],
    TaskType.ARCHITECTURE: ["firecrawl", "markitdown"],
    TaskType.SYSTEM_DESIGN: ["firecrawl"],
    TaskType.DOCUMENTATION: ["markitdown", "firecrawl"],
    TaskType.BUG_FIX: ["github"],
    TaskType.FEATURE: ["github"],
    TaskType.REFACTOR: ["github"],
    TaskType.RELEASE: ["github"],
    TaskType.DEPLOYMENT: ["github", "composio"],
    TaskType.REVIEW: ["github"],
    TaskType.TESTING: ["agent_memory"],
    TaskType.LARGE_PROJECT: ["agent_memory", "ruflo", "hermes"],
    TaskType.PROJECT_PLANNING: ["agent_memory"],
    TaskType.PERFORMANCE: ["agent_memory"],
}


class MCPSelector:
    def select(self, classification: ClassificationResult,
                selected_agents: List[str],
                selected_skills: List[str],
                context: Optional[Dict] = None) -> List[MCPDef]:
        selected_mcps: List[MCPDef] = []
        seen: Set[str] = set()

        task_mcps = MCP_TASK_MAP.get(classification.task_type, [])
        for mcp_name in task_mcps:
            if mcp_name not in seen:
                mcp = mcp_registry.get(mcp_name)
                if mcp and mcp.enabled:
                    selected_mcps.append(mcp)
                    seen.add(mcp_name)

        for skill in selected_skills:
            for mcp_name in getattr(skill, "required_mcps", []):
                if mcp_name not in seen:
                    mcp = mcp_registry.get(mcp_name)
                    if mcp and mcp.enabled:
                        selected_mcps.append(mcp)
                        seen.add(mcp_name)

        for agent_type in selected_agents:
            for mcp in mcp_registry.list():
                if mcp.name not in seen and agent_type in mcp.secondary_agents:
                    selected_mcps.append(mcp)
                    seen.add(mcp.name)

        return selected_mcps

    def select_by_agent(self, agent_type: str) -> List[MCPDef]:
        results = []
        for mcp in mcp_registry.list():
            if mcp.owner_agent == agent_type or agent_type in mcp.secondary_agents:
                results.append(mcp)
        return results


mcp_selector = MCPSelector()
