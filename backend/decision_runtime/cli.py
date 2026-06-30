import argparse
from typing import Any, Dict

from backend.decision_runtime import (
    runtime_engine, DecisionRequest, EnvironmentMode,
    decision_trace, escalation_manager, comm_enforcer,
    mode_controller,
)
from backend.decision_runtime.escalation import SeverityLevel


def cmd_decide(args):
    request = DecisionRequest(
        task=" ".join(args.task),
        source=args.source or "cli",
        mode=EnvironmentMode(args.mode) if args.mode else EnvironmentMode.BUILD,
        correlation_id=args.correlation_id,
    )
    result = runtime_engine.decide(request)
    _print_decision(result)


def cmd_trace(args):
    if args.id:
        t = decision_trace.get(args.id)
        if t:
            print(f"ID: {t.decision_id}")
            print(f"Task: {t.task}")
            print(f"Reason: {t.reason}")
            print(f"Confidence: {t.confidence}")
            print(f"Outcome: {t.outcome}")
            print(f"Owner: {t.owner}")
            print(f"Timestamp: {t.timestamp}")
        else:
            print(f"Trace {args.id} not found")
    else:
        s = decision_trace.summary()
        print(f"Total decisions: {s['total_decisions']}")
        print(f"By confidence: {s['by_confidence']}")
        print(f"By owner: {s['by_owner']}")
        traces = decision_trace.find(limit=args.limit or 10)
        for t in reversed(traces):
            print(f"  {t.decision_id}: {t.task[:60]} [{t.outcome}]")


def cmd_escalate(args):
    e = escalation_manager.escalate(
        task=" ".join(args.issue) if args.issue else args.desc,
        severity=SeverityLevel[args.severity.upper()] if args.severity else SeverityLevel.WARNING,
        impact=args.impact or "See description",
        source_agent=args.agent or "cli",
        evidence=args.evidence or [],
        recommendations=args.recommendations or [],
    )
    print(f"Escalation {e.escalation_id} created (level {e.escalation_level.value})")


def cmd_check_comm(args):
    result = comm_enforcer.check(args.sender, args.receiver)
    if result["allowed"]:
        print(f"{args.sender} -> {args.receiver}: ALLOWED")
    else:
        print(f"{args.sender} -> {args.receiver}: BLOCKED ({result['reason']})")
        print(f"Suggested route: {' -> '.join(result['suggested_route'])}")


def cmd_mode(args):
    if args.mode:
        mode = EnvironmentMode(args.mode)
        mode_controller.set_mode(mode)
    mode = mode_controller.mode
    print(f"Mode: {mode.value}")
    print(f"Priorities: {mode_controller.priorities()}")


def _print_decision(result: Dict[str, Any]):
    print(f"Status: {result['status']}")
    print(f"Mode: {result.get('mode', 'N/A')}")
    print(f"Priorities: {result.get('priorities', [])}")

    summary = result.get("summary", {})
    print(f"Task type: {summary.get('task_type', 'N/A')}")
    print(f"Complexity: {summary.get('complexity', 'N/A')}")

    agents = result.get("agents", {})
    selected = agents.get("selected", [])
    print(f"Selected agents: {selected}")

    skills = result.get("skills", {})
    selected_skills = skills.get("selected", [])
    print(f"Selected skills: {selected_skills}")

    model = result.get("model", {})
    print(f"Model: {model.get('selected', 'N/A')}")

    errors = result.get("errors", [])
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")


def main():
    parser = argparse.ArgumentParser(description="CAMera Decision Runtime CLI")
    parser.add_argument("--correlation-id", help="Correlation ID")
    sub = parser.add_subparsers(dest="command")

    p_decide = sub.add_parser("decide", help="Run a decision through the engine")
    p_decide.add_argument("task", nargs="+", help="Task description")
    p_decide.add_argument("--source", default="cli")
    p_decide.add_argument("--mode", choices=["teaching", "build", "autonomous"])
    p_decide.set_defaults(func=cmd_decide)

    p_trace = sub.add_parser("trace", help="View decision trace records")
    p_trace.add_argument("--id", help="Trace ID")
    p_trace.add_argument("--limit", type=int, default=10)
    p_trace.set_defaults(func=cmd_trace)

    p_esc = sub.add_parser("escalate", help="Create an escalation")
    p_esc.add_argument("desc", nargs="?", help="Issue description")
    p_esc.add_argument("--issue", nargs="+", help="Issue (multiple words)")
    p_esc.add_argument("--severity", choices=["informational", "warning", "significant_risk", "critical", "emergency"])
    p_esc.add_argument("--impact", help="Impact description")
    p_esc.add_argument("--agent", help="Source agent")
    p_esc.add_argument("--evidence", nargs="*")
    p_esc.add_argument("--recommendations", nargs="*")
    p_esc.set_defaults(func=cmd_escalate)

    p_comm = sub.add_parser("comm", help="Check allowed communication")
    p_comm.add_argument("sender", help="Source agent")
    p_comm.add_argument("receiver", help="Target agent")
    p_comm.set_defaults(func=cmd_check_comm)

    p_mode = sub.add_parser("mode", help="Get/set environment mode")
    p_mode.add_argument("mode", nargs="?", choices=["teaching", "build", "autonomous"])
    p_mode.set_defaults(func=cmd_mode)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
