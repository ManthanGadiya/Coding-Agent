import os
from typing import Optional
from backend.mcp import MCPClient, MCPResponse, register, log_use


class FirecrawlClient(MCPClient):
    def __init__(self):
        super().__init__(
            name="firecrawl",
            description="Scrape, search, and crawl websites"
        )
        self._api_key = os.getenv("FIRECRAWL_API_KEY", "")
        self._base = "https://api.firecrawl.dev/v1"

    async def execute(self, action: str, **kwargs) -> MCPResponse:
        import httpx
        url = kwargs.get("url", "")
        query = kwargs.get("query", "")

        if not self._api_key:
            return MCPResponse(success=False, error="FIRECRAWL_API_KEY not set")

        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                if action == "scrape":
                    resp = await client.post(f"{self._base}/scrape", json={"url": url}, headers=headers)
                elif action == "search":
                    resp = await client.post(f"{self._base}/search", json={"query": query}, headers=headers)
                elif action == "crawl":
                    resp = await client.post(f"{self._base}/crawl", json={"url": url, "maxDepth": kwargs.get("max_depth", 2)}, headers=headers)
                else:
                    return MCPResponse(success=False, error=f"Unknown action: {action}")

                data = resp.json()
                ok = resp.is_success
                log_use({"client": self.name, "action": action, "url": url, "status": resp.status_code})
                return MCPResponse(success=ok, data=data, metadata={"status": resp.status_code})
        except Exception as e:
            return MCPResponse(success=False, error=str(e))


class GitHubClient(MCPClient):
    def __init__(self):
        super().__init__(
            name="github",
            description="GitHub API: issues, PRs, repos, files, search"
        )
        self._token = os.getenv("GITHUB_TOKEN", "")
        self._base = "https://api.github.com"

    async def execute(self, action: str, **kwargs) -> MCPResponse:
        import httpx
        owner = kwargs.get("owner", "")
        repo = kwargs.get("repo", "")

        headers = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with httpx.AsyncClient(timeout=30, headers=headers) as client:
                if action == "list_issues":
                    resp = await client.get(f"{self._base}/repos/{owner}/{repo}/issues", params={"state": kwargs.get("state", "open"), "per_page": kwargs.get("per_page", 20)})
                elif action == "create_issue":
                    resp = await client.post(f"{self._base}/repos/{owner}/{repo}/issues", json={"title": kwargs["title"], "body": kwargs.get("body", "")})
                elif action == "list_prs":
                    resp = await client.get(f"{self._base}/repos/{owner}/{repo}/pulls", params={"state": kwargs.get("state", "open")})
                elif action == "get_file":
                    resp = await client.get(f"{self._base}/repos/{owner}/{repo}/contents/{kwargs['path']}")
                elif action == "search_code":
                    resp = await client.get(f"{self._base}/search/code", params={"q": kwargs["query"]})
                elif action == "list_branches":
                    resp = await client.get(f"{self._base}/repos/{owner}/{repo}/branches")
                else:
                    return MCPResponse(success=False, error=f"Unknown action: {action}")

                data = resp.json()
                log_use({"client": self.name, "action": action, "owner": owner, "repo": repo, "status": resp.status_code})
                return MCPResponse(success=resp.is_success, data=data, metadata={"status": resp.status_code})
        except Exception as e:
            return MCPResponse(success=False, error=str(e))


class MarkItDownClient(MCPClient):
    def __init__(self):
        super().__init__(
            name="markitdown",
            description="Convert documents (PDF, DOCX, XLSX, images, audio, HTML, CSV, JSON) to markdown"
        )

    async def execute(self, action: str, **kwargs) -> MCPResponse:
        from markitdown import MarkItDown
        md = MarkItDown()
        file_path = kwargs.get("file_path", "")
        url = kwargs.get("url", "")

        try:
            if action == "convert_file":
                if not file_path:
                    return MCPResponse(success=False, error="No file_path provided")
                result = md.convert(file_path)
                log_use({"client": self.name, "action": action, "file": file_path})
                return MCPResponse(success=True, data=result.text_content,
                                   metadata={"file": file_path, "title": result.title})

            elif action == "convert_url":
                if not url:
                    return MCPResponse(success=False, error="No url provided")
                import httpx
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    resp = await client.get(url)
                    import tempfile, os
                    suffix = os.path.splitext(url.split("/")[-1].split("?")[0])[1] or ".html"
                    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                        f.write(resp.content)
                        tmp = f.name
                    try:
                        result = md.convert(tmp)
                    finally:
                        os.unlink(tmp)
                log_use({"client": self.name, "action": action, "url": url})
                return MCPResponse(success=True, data=result.text_content, metadata={"url": url, "title": result.title})

            else:
                return MCPResponse(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            return MCPResponse(success=False, error=str(e))


register(FirecrawlClient())
register(GitHubClient())
register(MarkItDownClient())
