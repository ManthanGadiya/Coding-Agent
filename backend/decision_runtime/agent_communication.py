from typing import Dict, List, Set, Tuple

from backend.decision_runtime.event_bus import event_bus, Event, EventPriority


AGENTS = [
    "manager", "architect", "planner", "coder",
    "tester", "debugger", "reviewer", "memory",
]

ALLOWED_PATHS: Set[Tuple[str, str]] = {
    ("manager", "architect"),
    ("manager", "planner"),
    ("manager", "coder"),
    ("manager", "tester"),
    ("manager", "debugger"),
    ("manager", "reviewer"),
    ("manager", "memory"),
    ("architect", "manager"),
    ("architect", "planner"),
    ("planner", "architect"),
    ("planner", "manager"),
    ("planner", "coder"),
    ("coder", "planner"),
    ("coder", "tester"),
    ("coder", "debugger"),
    ("tester", "coder"),
    ("tester", "debugger"),
    ("tester", "reviewer"),
    ("tester", "manager"),
    ("debugger", "tester"),
    ("debugger", "coder"),
    ("debugger", "manager"),
    ("reviewer", "tester"),
    ("reviewer", "manager"),
}


ALLOWED_PATHS.update({("memory", a) for a in AGENTS})
ALLOWED_PATHS.update({(a, "memory") for a in AGENTS})


class CommunicationViolation(Exception):
    def __init__(self, sender: str, receiver: str, reason: str):
        self.sender = sender
        self.receiver = receiver
        self.reason = reason
        super().__init__(f"{sender} -> {receiver}: {reason}")


class CommunicationEnforcer:
    def __init__(self):
        self._violations: List[Dict] = []

    def check(self, sender: str, receiver: str,
              suggest_route: bool = True) -> Dict:
        sender_n = sender.lower().strip()
        receiver_n = receiver.lower().strip()

        if sender_n not in AGENTS:
            raise ValueError(f"Unknown agent: {sender}")
        if receiver_n not in AGENTS:
            raise ValueError(f"Unknown agent: {receiver}")

        path = (sender_n, receiver_n)
        allowed = path in ALLOWED_PATHS
        result = {"allowed": allowed, "sender": sender_n, "receiver": receiver_n}

        if not allowed:
            route = self._suggest_route(sender_n) if suggest_route else []
            result["violation"] = True
            result["suggested_route"] = route
            result["reason"] = f"Direct {sender_n}->{receiver_n} not permitted"
            self._violations.append(result)

            event_bus.publish(Event(
                topic="communication.violation",
                source="agent_communication",
                data=result,
                priority=EventPriority.HIGH,
            ))

        return result

    def enforce(self, sender: str, receiver: str):
        result = self.check(sender, receiver)
        if not result["allowed"]:
            raise CommunicationViolation(
                sender, receiver, result["reason"]
            )
        return result

    def _suggest_route(self, agent: str) -> List[str]:
        if agent == "memory":
            return [agent]
        if agent in ("reviewer", "debugger", "tester", "coder"):
            return [agent, "manager"]
        if agent == "planner":
            return [agent, "architect", "manager"]
        if agent == "architect":
            return [agent, "manager"]
        return [agent, "manager"]

    def suggest_path(self, sender: str, receiver: str) -> List[str]:
        result = self.check(sender, receiver, suggest_route=False)
        if result["allowed"]:
            return [sender, receiver]
        return self._suggest_route(sender) + [receiver]

    def violations(self, limit: int = 50) -> List[Dict]:
        return self._violations[-limit:]

    def allowed(self, sender: str) -> List[str]:
        return [r for (s, r) in ALLOWED_PATHS if s == sender.lower().strip()]

    def can_communicate(self, sender: str, receiver: str) -> bool:
        return (sender.lower().strip(), receiver.lower().strip()) in ALLOWED_PATHS


comm_enforcer = CommunicationEnforcer()
