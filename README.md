# CAMera

Cognitive Autonomous Multi-Agent Engineering Reasoning Assistant

## Architecture

```
camera/
├── agent-docs/          # Governance, architecture, agent definitions
├── backend/             # FastAPI backend
│   ├── agents/          # 6 specialized agents + orchestrator
│   ├── api/             # REST endpoints (projects, tasks, agents, memory, workflows)
│   ├── core/            # Database engine, config
│   ├── models/          # SQLAlchemy ORM models
│   ├── tools/           # Tool abstraction layer
│   └── main.py          # App entry point
├── frontend/            # Next.js UI (pending)
└── pyproject.toml
```

## Agents

| Agent | Role |
|---|---|
| **Orchestrator** | Routes tasks, manages workflows, resolves conflicts |
| **Coder** | Creates/modifies files, runs builds/tests |
| **Reviewer** | Static analysis, security checks, architecture review |
| **Tester** | Writes/runs tests, reports coverage |
| **Memory** | Stores/retrieves/prunes long-term knowledge |
| **Debugger** | Diagnoses errors, analyzes traces, suggests fixes |

## Quick Start

```bash
pip install -e .
uvicorn backend.main:app --reload
```

## Design

Governance-driven multi-agent system. Seven agents coordinate via the Orchestrator through defined workflows. Memory agent provides cross-session context. All behavior follows the hierarchy in `agent-docs/`: Constitution → Architecture → Decision Engine → Agents → Memory → Workflows → Autonomy → Tools → Learning → User.
