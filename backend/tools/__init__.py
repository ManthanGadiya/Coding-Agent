from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ToolPermission(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


class ToolRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    def __init__(self, name: str, description: str, required_permissions: List[ToolPermission], risk_level: ToolRiskLevel = ToolRiskLevel.LOW):
        self.name = name
        self.description = description
        self.required_permissions = required_permissions
        self.risk_level = risk_level
        self._autonomy_check = None

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass

    def check_permissions(self, agent_capabilities: List[str]) -> bool:
        return all(p.value in agent_capabilities for p in self.required_permissions)

    def validate_args(self, kwargs: Dict, required_args: List[str]) -> Optional[str]:
        for arg in required_args:
            if arg not in kwargs:
                return f"Missing required argument: {arg}"
        return None

    async def safe_execute(self, agent_id: str = "", agent_role: str = "",
                            session_id: str = "", **kwargs) -> ToolResult:
        result = await self.execute(**kwargs)
        log_tool_use({
            "tool": self.name, "agent_id": agent_id, "agent_role": agent_role,
            "session_id": session_id, "params": {k: v for k, v in kwargs.items()
                                                  if k not in ("content", "password", "secret")},
            "success": result.success, "risk_level": self.risk_level.value,
        })
        return result


class FileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="file_tool",
            description="Read and write files on the local filesystem",
            required_permissions=[ToolPermission.READ, ToolPermission.WRITE],
            risk_level=ToolRiskLevel.MEDIUM
        )

    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "read")
        path = kwargs.get("path", "")
        content = kwargs.get("content")
        pattern = kwargs.get("pattern", "")
        max_results = kwargs.get("max_results", 50)

        if action == "read":
            return self._read(path)
        elif action == "write":
            return self._write(path, content)
        elif action == "delete":
            return self._delete(path)
        elif action == "search":
            return self._search(path, pattern, max_results)
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")

    def _search(self, path: str, pattern: str, max_results: int = 50) -> ToolResult:
        import re
        try:
            from pathlib import Path
            base = Path(path)
            if not base.exists():
                return ToolResult(success=False, error=f"Path does not exist: {path}")
            matches = []
            for f in base.rglob("*"):
                if not f.is_file():
                    continue
                try:
                    content = f.read_text(errors="ignore")
                    if re.search(pattern, content, re.IGNORECASE):
                        matches.append(str(f.relative_to(base)))
                        if len(matches) >= max_results:
                            break
                except Exception:
                    continue
            return ToolResult(success=True, data=matches,
                              metadata={"total": len(matches), "pattern": pattern, "root": path})
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _read(self, path: str) -> ToolResult:
        try:
            with open(path) as f:
                return ToolResult(success=True, data=f.read())
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _write(self, path: str, content: str) -> ToolResult:
        try:
            from pathlib import Path
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return ToolResult(success=True, data=f"Written {len(content)} bytes")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _delete(self, path: str) -> ToolResult:
        try:
            from pathlib import Path
            Path(path).unlink()
            return ToolResult(success=True, data=f"Deleted {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class CommandTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="command_tool",
            description="Execute shell commands",
            required_permissions=[ToolPermission.EXECUTE],
            risk_level=ToolRiskLevel.HIGH
        )

    async def execute(self, **kwargs) -> ToolResult:
        import subprocess
        cmd = kwargs.get("command", "")
        cwd = kwargs.get("cwd", ".")
        timeout = kwargs.get("timeout", 300)

        if not cmd:
            return ToolResult(success=False, error="No command provided")

        try:
            result = subprocess.run(
                cmd if isinstance(cmd, list) else cmd.split(),
                capture_output=True, text=True, cwd=cwd, timeout=timeout
            )
            return ToolResult(
                success=result.returncode == 0,
                data=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                metadata={"returncode": result.returncode}
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error=f"Command timed out after {timeout}s")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GitTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="git_tool",
            description="Execute git operations (status, log, diff, add, commit, push, pull)",
            required_permissions=[ToolPermission.READ, ToolPermission.EXECUTE],
            risk_level=ToolRiskLevel.MEDIUM
        )

    async def execute(self, **kwargs) -> ToolResult:
        import subprocess
        action = kwargs.get("action", "status")
        repo = kwargs.get("repo", ".")
        safe_actions = {"status", "log", "diff", "show", "branch", "remote"}

        if action not in safe_actions and action not in ("add", "commit", "push", "pull", "checkout", "merge"):
            return ToolResult(success=False, error=f"Action '{action}' requires ADMIN permission")

        cmd = ["git", "-C", repo, action]
        if action == "log":
            cmd.extend(["--oneline", "-10"])
        elif action == "add":
            cmd.append(kwargs.get("file", "."))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return ToolResult(success=result.returncode == 0, data=result.stdout or result.stderr, metadata={"returncode": result.returncode})
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class DatabaseTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="database_tool",
            description="Execute SQL queries against project databases",
            required_permissions=[ToolPermission.READ, ToolPermission.EXECUTE],
            risk_level=ToolRiskLevel.HIGH
        )

    async def execute(self, **kwargs) -> ToolResult:
        conn_str = kwargs.get("connection", "")
        query = kwargs.get("query", "")
        if not query:
            return ToolResult(success=False, error="No query provided")
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(conn_str) if conn_str else None
            if engine:
                with engine.connect() as conn:
                    result = conn.execute(text(query))
                    if query.strip().upper().startswith("SELECT"):
                        rows = [dict(r._mapping) for r in result]
                        return ToolResult(success=True, data=rows, metadata={"row_count": len(rows)})
                    conn.commit()
                    return ToolResult(success=True, data=f"Query executed, {result.rowcount} rows affected")
            return ToolResult(success=False, error="No database connection configured")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class DockerTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="docker_tool",
            description="Manage Docker containers, images, and compose stacks",
            required_permissions=[ToolPermission.EXECUTE],
            risk_level=ToolRiskLevel.HIGH
        )

    async def execute(self, **kwargs) -> ToolResult:
        import subprocess
        action = kwargs.get("action", "ps")
        name = kwargs.get("name", "")
        safe_actions = {"ps", "images", "logs", "inspect", "stats"}

        cmd = ["docker"]
        if action == "ps":
            cmd.extend(["ps", "-a"])
        elif action == "images":
            cmd.append("images")
        elif action == "logs":
            cmd.extend(["logs", "--tail", "50", name])
        elif action not in safe_actions:
            return ToolResult(success=False, error=f"Action '{action}' requires explicit approval")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return ToolResult(success=result.returncode == 0, data=result.stdout, metadata={"returncode": result.returncode})
        except FileNotFoundError:
            return ToolResult(success=False, error="Docker not available")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class WebTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="web_tool",
            description="Web search, documentation lookup, research with source evaluation",
            required_permissions=[ToolPermission.READ],
            risk_level=ToolRiskLevel.LOW
        )

    async def execute(self, **kwargs) -> ToolResult:
        import httpx
        action = kwargs.get("action", "fetch")
        url = kwargs.get("url", "")
        query = kwargs.get("query", "")

        if action == "fetch":
            return await self._fetch(url)
        elif action == "search":
            return await self._search_web(query)
        elif action == "docs":
            return await self._lookup_docs(url or query)
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")

    async def _fetch(self, url: str) -> ToolResult:
        if not url:
            return ToolResult(success=False, error="No URL provided")
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                resp = await client.get(url)
                return ToolResult(success=resp.is_success, data=resp.text[:200000],
                                  metadata={"status": resp.status_code, "url": url,
                                            "content_type": resp.headers.get("content-type")})
        except httpx.TimeoutException:
            return ToolResult(success=False, error="Request timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def _search_web(self, query: str) -> ToolResult:
        if not query:
            return ToolResult(success=False, error="No search query")
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                resp = await client.get("https://html.duckduckgo.com/html/",
                                        params={"q": query},
                                        headers={"User-Agent": "Mozilla/5.0"})
                if resp.is_success:
                    import re
                    results = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', resp.text)
                    return ToolResult(success=True,
                                      data=[{"title": r[1], "url": r[0]} for r in results[:10]],
                                      metadata={"query": query, "result_count": len(results[:10])})
                return ToolResult(success=False, error=f"Search failed: HTTP {resp.status_code}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def _lookup_docs(self, target: str) -> ToolResult:
        urls = {
            "fastapi": "https://fastapi.tiangolo.com",
            "sqlalchemy": "https://docs.sqlalchemy.org",
            "nextjs": "https://nextjs.org/docs",
            "react": "https://react.dev",
            "python": "https://docs.python.org/3",
        }
        url = urls.get(target.lower(), target if target.startswith("http") else None)
        if not url:
            return self._search_web(f"{target} documentation")
        return await self._fetch(url)


TOOL_REGISTRY: Dict[str, BaseTool] = {
    "file": FileTool(),
    "command": CommandTool(),
    "web": WebTool(),
    "git": GitTool(),
    "database": DatabaseTool(),
    "docker": DockerTool(),
}


AUDIT_LOG: List[Dict] = []


def log_tool_use(entry: Dict):
    entry["timestamp"] = datetime.utcnow().isoformat()
    AUDIT_LOG.append(entry)


def get_tool_audit_log(limit: int = 50) -> List[Dict]:
    return AUDIT_LOG[-limit:]


def get_tool(name: str) -> Optional[BaseTool]:
    return TOOL_REGISTRY.get(name)