# CAMera

## Autonomous Multi-Agent Software Engineering System

CAMera is a governance-driven multi-agent software engineering system — a coordinated engineering organization of specialized agents with defined responsibilities, workflows, memory, and governance.

---

## Current Status

Active development. Backend + frontend working.

### Backend (FastAPI, port 8000)
- **149 API routes** across projects, tasks, agents, memory, workflows, LLM, decisions, learning, autonomy, tools
- **8 agents**: Manager (coordinator), Architect, Planner, Coder, Reviewer, Tester, Debugger, Memory — all wired to **ModelRouter** for real LLM output (not stubs)
- **CoderAgent._implement()** writes files to disk from LLM output (parses fenced code blocks with paths)
- **SafetyController** wired into BaseAgent.execute_task() — blocks dangerous ops pre-execution
- **6 tools** (file, command, web, git, database, docker) accessible via BaseAgent._run_tool()
- **Auto-lessons**: ManagerAgent.run_goal() auto-generates learning lesson on step failure
- **ModelRouter**: 5 providers — Ollama (local), OpenAI, Anthropic, Gemini, OpenAI-compatible gateway (OpenRouter/LiteLLM/etc.)
- **Streaming endpoint**: `POST /api/v1/llm/stream` for token-by-token LLM output
- **Workflow Engine**: 6 workflow types, 4 complexity tiers, task classifier, step builder
- **Learning System**: Failure analysis, lessons learned, metrics, improvement proposals — **persisted to SQLAlchemy**
- **Knowledge Engine**: Observations, knowledge artifacts, candidate rules — **persisted**
- **Disagreement Engine**: Strategic/operational classification, notifications, resolution — **persisted**
- **Decision Engine**: 8-step evidence-based workflow with confidence scoring
- **Autonomy System**: 3 modes, 35+ capability risk levels, 4-tier approval classes
- **Weighted Memory Retrieval**: 7-factor scoring, 8 agent profiles, 9 retrieval modes
- **TypeScript interfaces**: All backend API responses typed in frontend (replaced all `any`)
- **Memory auto-retention**: Retention+compression hooks auto-trigger on memory writes when count > 200
- **Database**: SQLAlchemy + SQLite, auto-seeded at startup
- **Release Engine**: DB-backed ReleaseCandidate model, 4 check gates, 4 rollback strategies

### Frontend (Next.js 16, port 3000)
- **8 pages**: Dashboard, Projects, Agents, Tasks, Workflows, Memory, Memory Retrieval, Learning
- **Wired**: Tasks and Memory pages fetch from real API
- **Dashboard**: Includes goal runner with `run_goal()` integration
- **Dark industrial theme**, Tailwind CSS, lucide-react

### Manager Runtime (run_goal)
- `ManagerAgent.run_goal(goal)`: classify → complexity → smallest workflow → execute → result
- Step-to-agent mapping for all 28 workflow step types
- Each step result auto-stored to MemoryAgent for cross-session recall
- ManagerAgent is a singleton — state persists across calls

---

## Quick Start

```bash
# Backend
cd backend
uvicorn backend.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

Configure `.env` in `backend/` with API keys for cloud providers:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
OPENAI_COMPATIBLE_BASE_URL=https://openrouter.ai/api/v1
OPENAI_COMPATIBLE_API_KEY=sk-...
```

---

## Providers

| Provider | Config Key | When Available |
|----------|-----------|----------------|
| Ollama | `OLLAMA_BASE_URL` | Always |
| OpenAI | `OPENAI_API_KEY` | Set |
| Anthropic | `ANTHROPIC_API_KEY` | Set |
| Gemini | `GEMINI_API_KEY` | Set |
| Gateway | `OPENAI_COMPATIBLE_*` | Both URL + key set |

---

## Guiding Philosophy

1. Correctness → Quality → Safety → Reliability → Efficiency
2. Multi-agent collaboration over monolithic agents
3. Governance before autonomy
4. User is the final decision maker
5. Learn from failures, adopt through governance

---

## Agent Docs

Full architecture, constitution, workflows, and governance in `agent-docs/` (54 files across 9 directories).
