from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


@dataclass
class MCPResponse:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TransportType(str, Enum):
    STDIO = "stdio"
    SSE = "sse"


@dataclass
class MCPServerConfig:
    name: str
    transport: TransportType
    command: str = ""
    args: List[str] = field(default_factory=list)
    url: str = ""
    env: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True


_SERVER_REGISTRY: Dict[str, MCPServerConfig] = {}
_CONNECTED_CLIENTS: Dict[str, Any] = {}
_MCP_LOG: List[Dict] = []


def register_server(config: MCPServerConfig):
    _SERVER_REGISTRY[config.name] = config


def remove_server(name: str):
    _SERVER_REGISTRY.pop(name, None)
    _CONNECTED_CLIENTS.pop(name, None)


def get_server(name: str) -> Optional[MCPServerConfig]:
    return _SERVER_REGISTRY.get(name)


def list_servers() -> List[Dict]:
    return [{"name": s.name, "transport": s.transport.value, "enabled": s.enabled} for s in _SERVER_REGISTRY.values()]


def list_connected() -> List[str]:
    return list(_CONNECTED_CLIENTS.keys())


def log_use(entry: Dict):
    entry["timestamp"] = datetime.utcnow().isoformat()
    _MCP_LOG.append(entry)


def get_log(limit: int = 50) -> List[Dict]:
    return _MCP_LOG[-limit:]
