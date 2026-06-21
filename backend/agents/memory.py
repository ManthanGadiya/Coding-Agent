from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent, AgentTask, AgentResult, AgentMessage
from backend.core.database import SessionLocal
from backend.models.memory import ProjectMemory, MemoryCategory, ConfidenceLevel
from backend.models.project import Project


class MemoryAgent(BaseAgent):
    def __init__(self, agent_id: str = "memory-1", config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            name="Memory Agent",
            capabilities=[
                "store", "retrieve", "search", "prune",
                "get_context", "list_by_project"
            ],
            config=config
        )

    async def process_task(self, task: AgentTask) -> AgentResult:
        task_type = task.task_type
        data = task.input_data

        if task_type == "store":
            return self._store(data)
        elif task_type == "retrieve":
            return self._retrieve(data)
        elif task_type == "search":
            return self._search(data)
        elif task_type == "prune":
            return self._prune(data)
        elif task_type == "get_context":
            return self._get_context(data)
        elif task_type == "list_by_project":
            return self._list_by_project(data)
        else:
            return AgentResult(
                task_id=task.task_id,
                success=False,
                error=f"Unknown memory type: {task_type}"
            )

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        if message.message_type == "query":
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=f"MemoryAgent ready. Capabilities: {', '.join(self.capabilities)}",
                message_type="response"
            )
        return None

    def _get_db(self) -> Session:
        return SessionLocal()

    def _store(self, data: Dict) -> AgentResult:
        db = self._get_db()
        try:
            entry = ProjectMemory(
                project_id=data.get("project_id"),
                category=data.get("category", MemoryCategory.KNOWLEDGE),
                key=data.get("key"),
                value=data.get("value"),
                context=data.get("context"),
                tags=data.get("tags"),
                confidence=data.get("confidence", ConfidenceLevel.MEDIUM)
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return AgentResult(
                task_id="",
                success=True,
                output=f"Stored memory: {entry.id}",
                metadata={"memory_id": entry.id}
            )
        except Exception as e:
            db.rollback()
            return AgentResult(task_id="", success=False, error=str(e))
        finally:
            db.close()

    def _retrieve(self, data: Dict) -> AgentResult:
        db = self._get_db()
        try:
            query = db.query(ProjectMemory)
            if data.get("memory_id"):
                entry = query.filter(ProjectMemory.id == data["memory_id"]).first()
            elif data.get("key"):
                entry = query.filter(
                    ProjectMemory.key == data["key"],
                    ProjectMemory.project_id == data.get("project_id")
                ).order_by(ProjectMemory.created_at.desc()).first()
            else:
                return AgentResult(task_id="", success=False, error="memory_id or key required")

            if not entry:
                return AgentResult(task_id="", success=True, output=None)

            return AgentResult(
                task_id="",
                success=True,
                output={"key": entry.key, "value": entry.value, "category": entry.category, "tags": entry.tags}
            )
        finally:
            db.close()

    def _search(self, data: Dict) -> AgentResult:
        db = self._get_db()
        try:
            query = db.query(ProjectMemory)
            if data.get("project_id"):
                query = query.filter(ProjectMemory.project_id == data["project_id"])
            if data.get("category"):
                query = query.filter(ProjectMemory.category == data["category"])
            if data.get("tags"):
                query = query.filter(ProjectMemory.tags.overlap(data["tags"]))
            if data.get("query_text"):
                # ponytail: simple LIKE search, use FTS when scale demands it
                query = query.filter(ProjectMemory.value.ilike(f"%{data['query_text']}%"))

            results = query.order_by(ProjectMemory.importance.desc()).limit(data.get("limit", 20)).all()
            return AgentResult(
                task_id="",
                success=True,
                output=[{"key": r.key, "value": r.value, "category": r.category, "tags": r.tags} for r in results],
                metadata={"count": len(results)}
            )
        finally:
            db.close()

    def _prune(self, data: Dict) -> AgentResult:
        db = self._get_db()
        try:
            cutoff = datetime.utcnow() - timedelta(days=data.get("retention_days", 365))
            stale = db.query(ProjectMemory).filter(
                ProjectMemory.created_at < cutoff,
                ProjectMemory.status == "active"
            ).all()

            for entry in stale:
                entry.status = "archived"

            db.commit()
            return AgentResult(
                task_id="",
                success=True,
                output=f"Archived {len(stale)} stale entries",
                metadata={"archived": len(stale)}
            )
        finally:
            db.close()

    def _get_context(self, data: Dict) -> AgentResult:
        project_id = data.get("project_id")
        db = self._get_db()
        try:
            entries = db.query(ProjectMemory).filter(
                ProjectMemory.project_id == project_id,
                ProjectMemory.status == "active"
            ).order_by(ProjectMemory.importance.desc()).limit(data.get("limit", 10)).all()

            context = "\n".join(f"- [{e.category}] {e.key}: {str(e.value)[:200]}" for e in entries)
            return AgentResult(
                task_id="",
                success=True,
                output=context,
                metadata={"entry_count": len(entries)}
            )
        finally:
            db.close()

    def _list_by_project(self, data: Dict) -> AgentResult:
        db = self._get_db()
        try:
            entries = db.query(ProjectMemory).filter(
                ProjectMemory.project_id == data.get("project_id")
            ).order_by(ProjectMemory.created_at.desc()).limit(data.get("limit", 50)).all()

            return AgentResult(
                task_id="",
                success=True,
                output=[{"id": e.id, "key": e.key, "category": e.category, "tags": e.tags, "created_at": str(e.created_at)} for e in entries],
                metadata={"count": len(entries)}
            )
        finally:
            db.close()