from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    level: LogLevel
    topic: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    correlation_id: Optional[str] = None
    timestamp: str = ""


class DecisionLogger:
    def __init__(self, max_entries: int = 1000):
        self._entries: List[LogEntry] = []
        self._max_entries = max_entries

    def log(self, level: LogLevel, topic: str, message: str, data: Optional[Dict] = None,
            source: str = "", correlation_id: Optional[str] = None):
        entry = LogEntry(
            level=level,
            topic=topic,
            message=message,
            data=data or {},
            source=source,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow().isoformat(),
        )
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries.pop(0)

    def info(self, topic: str, message: str, **kwargs):
        self.log(LogLevel.INFO, topic, message, **kwargs)

    def warn(self, topic: str, message: str, **kwargs):
        self.log(LogLevel.WARN, topic, message, **kwargs)

    def error(self, topic: str, message: str, **kwargs):
        self.log(LogLevel.ERROR, topic, message, **kwargs)

    def debug(self, topic: str, message: str, **kwargs):
        self.log(LogLevel.DEBUG, topic, message, **kwargs)

    def critical(self, topic: str, message: str, **kwargs):
        self.log(LogLevel.CRITICAL, topic, message, **kwargs)

    def get_recent(self, limit: int = 50, level: Optional[LogLevel] = None,
                   topic: Optional[str] = None) -> List[LogEntry]:
        results = list(self._entries)
        if level:
            results = [e for e in results if e.level == level]
        if topic:
            results = [e for e in results if e.topic == topic]
        return results[-limit:]

    def get_by_correlation(self, correlation_id: str) -> List[LogEntry]:
        return [e for e in self._entries if e.correlation_id == correlation_id]

    def summary(self) -> Dict[str, Any]:
        by_level = {}
        for entry in self._entries:
            by_level[entry.level.value] = by_level.get(entry.level.value, 0) + 1
        by_topic = {}
        for entry in self._entries:
            by_topic[entry.topic] = by_topic.get(entry.topic, 0) + 1
        return {
            "total_entries": len(self._entries),
            "by_level": by_level,
            "by_topic": by_topic,
        }


decision_logger = DecisionLogger()
