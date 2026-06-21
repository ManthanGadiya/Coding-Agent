from typing import Any, Dict, List, Optional
from datetime import datetime

PREFIXES = {
    "memory": "MEM", "decision": "DEC", "bug": "BUG",
    "lesson": "LES", "risk": "RISK", "milestone": "MS",
    "artifact": "ART", "contradiction": "CON",
}


def _toon_value(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        return v.replace("\n", "\\n")
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v)


def toon_dumps(obj: Dict, indent: int = 0) -> str:
    pad = " " * indent
    lines = []
    for k, v in obj.items():
        key = k.replace(" ", "_")
        if isinstance(v, dict):
            lines.append(f"{pad}{key}:")
            lines.append(toon_dumps(v, indent + 1))
        elif isinstance(v, list):
            lines.append(f"{pad}{key}:")
            for item in v:
                if isinstance(item, dict):
                    sub = toon_dumps(item, indent + 1)
                    lines.append(sub)
                else:
                    lines.append(f"{' ' * (indent + 1)}- {_toon_value(item)}")
        else:
            lines.append(f"{pad}{key}: {_toon_value(v)}")
    return "\n".join(lines)


def _parse_scalar(val: str) -> Any:
    val = val.strip()
    if val == "null":
        return None
    if val == "true":
        return True
    if val == "false":
        return False
    if val == "[]":
        return []
    val = val.replace("\\n", "\n")
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


class _Parser:
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.pos = 0

    def peek(self) -> Optional[str]:
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            if line.strip() and not line.strip().startswith("#"):
                return line
            self.pos += 1
        return None

    def consume(self) -> Optional[str]:
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            self.pos += 1
            if line.strip() and not line.strip().startswith("#"):
                return line
        return None

    def indent_of(self, line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def parse_value(self, indent: int) -> Any:
        line = self.peek()
        if line is None:
            return None
        line_indent = self.indent_of(line)

        if line_indent < indent:
            return None
        if line_indent > indent:
            return None

        stripped = self.consume().strip()
        if stripped.startswith("- "):
            items = []
            items.append(_parse_scalar(stripped[2:]))
            while True:
                nxt = self.peek()
                if nxt is None or self.indent_of(nxt) != indent or not nxt.lstrip(" ").startswith("- "):
                    break
                items.append(_parse_scalar(self.consume().strip()[2:]))
            return items

        if stripped.endswith(":"):
            key = stripped[:-1].strip()
            result = {}
            list_val = None
            while True:
                child = self.parse_value(indent + 1)
                if child is None:
                    break
                if isinstance(child, tuple):
                    k, v = child
                    result[k] = v
                elif isinstance(child, list):
                    list_val = child
                elif isinstance(child, dict):
                    result.update(child)
            if list_val is not None and not result:
                return (key, list_val)
            return {key: result} if result else {key: list_val} if list_val is not None else {key: {}}

        if ": " in stripped:
            k, v = stripped.split(": ", 1)
            return (k.strip(), _parse_scalar(v))

        return None

    def parse(self) -> Dict:
        result = {}
        while True:
            val = self.parse_value(0)
            if val is None:
                break
            if isinstance(val, tuple):
                k, v = val
                result[k] = v
            elif isinstance(val, dict):
                result.update(val)
        return result


def toon_loads(text: str) -> Dict:
    return _Parser(text.strip().split("\n")).parse()


def generate_id(prefix_key: str = "memory") -> str:
    prefix = PREFIXES.get(prefix_key, "MEM")
    num = int(datetime.utcnow().timestamp() * 1000) % 100000
    return f"{prefix}-{num:05d}"


def memory_to_toon(memory: Dict) -> str:
    doc = {
        "id": memory.get("id", generate_id()),
        "type": memory.get("type", "memory"),
        "title": memory.get("title", ""),
        "content": memory.get("content", ""),
    }
    for f in ["context", "confidence", "source", "evidence", "relationships", "metadata"]:
        if f in memory and memory[f]:
            doc[f] = memory[f]
    return toon_dumps({"memory": doc})


def toon_to_memory(text: str) -> Dict:
    return toon_loads(text).get("memory", {})


def toon_to_json(text: str) -> Dict:
    return toon_loads(text)


def json_to_toon(obj: Dict) -> str:
    return toon_dumps(obj)
