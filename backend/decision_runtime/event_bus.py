from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
import traceback


class EventPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Event:
    topic: str
    data: Dict[str, Any]
    source: str
    priority: EventPriority = EventPriority.NORMAL
    timestamp: str = ""
    correlation_id: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


EventHandler = Callable[[Event], None]


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._history: List[Event] = []
        self._max_history = 1000

    def subscribe(self, topic: str, handler: EventHandler):
        self._subscribers.setdefault(topic, []).append(handler)

    def unsubscribe(self, topic: str, handler: EventHandler):
        handlers = self._subscribers.get(topic, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: Event):
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        handlers = self._subscribers.get(event.topic, []) + self._subscribers.get("*", [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                traceback.print_exc()

    async def publish_async(self, event: Event):
        self.publish(event)

    def get_history(self, topic: Optional[str] = None, limit: int = 50) -> List[Event]:
        if topic:
            return [e for e in self._history if e.topic == topic][-limit:]
        return self._history[-limit:]

    def clear(self):
        self._history.clear()


event_bus = EventBus()
