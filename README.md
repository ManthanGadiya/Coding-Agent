# CAMera

## Autonomous Multi-Agent Software Engineering System

CAMera is a governance-driven multi-agent software engineering system designed to plan, architect, implement, test, debug, review, learn, and improve software projects while remaining aligned with engineering quality and user goals.

Unlike traditional coding assistants, CAMera is designed to operate as a coordinated engineering organization composed of specialized agents with defined responsibilities, workflows, memory systems, and governance rules.

---

## Vision

The goal of CAMera is to create a highly capable engineering system capable of:

* Understanding projects deeply
* Maintaining long-term context
* Coordinating specialized agents
* Producing high-quality software
* Learning from successes and failures
* Adapting to user goals
* Preserving architectural consistency

CAMera prioritizes:

1. Correctness
2. Quality
3. Safety
4. Reliability
5. Efficiency

Speed is valuable.

Quality is mandatory.

---

## What Makes CAMera Different

CAMera is built around the idea that software engineering is not a single task but a collection of specialized responsibilities.

Rather than relying on one general-purpose agent, CAMera coordinates multiple specialized agents that collaborate to solve problems, evaluate decisions, review outcomes, and improve over time.

Key characteristics include:

* Multi-agent collaboration
* Governance-driven decision making
* Long-term memory and context retention
* Continuous learning and improvement
* User-aligned behavior
* Strong emphasis on software quality

---

## Core Principles

### Governance Before Autonomy

CAMera is not designed to behave as an uncontrolled autonomous system.

Learning does not imply adoption.

Behavior changes require governance and review.

---

### User Alignment

The user remains the final decision maker.

CAMera may:

* Recommend
* Explain
* Challenge
* Clarify

CAMera may not:

* Override
* Manipulate
* Enforce

---

### Learning Through Experience

CAMera continuously learns from:

* Successes
* Failures
* Reviews
* Feedback

Failures receive higher analytical priority because they reveal weaknesses, assumptions, and improvement opportunities.

---

### Engineering Excellence

CAMera values:

* Maintainability
* Testability
* Reliability
* Documentation
* Architectural Consistency

over short-term convenience.

---

## Learning and Improvement

CAMera is designed to improve through structured reflection and analysis.

The system evaluates outcomes, identifies mistakes, captures lessons learned, and uses those insights to improve future decisions.

Learning is intended to be:

* Transparent
* Reviewable
* Governed
* Aligned with user goals

The objective is not simply to accumulate knowledge, but to become more effective, reliable, and consistent over time.

---

## Human-Centered Design

CAMera is built to work with people, not replace them.

The system is intended to:

* Assist decision making
* Accelerate development
* Improve software quality
* Reduce repetitive work
* Support learning and understanding

Human oversight remains essential for strategic decisions, governance changes, and major project direction.

---

## Current Status

CAMera is in active development with a working backend and frontend.

### Backend (FastAPI)
- **60+ API routes** across projects, tasks, agents, memory, workflows, LLM, decisions, and autonomy
- **8 agents**: Manager (central coordinator), Architect, Planner, Coder, Reviewer, Tester, Debugger, Memory Agent
- **Decision Engine**: 8-step evidence-based decision workflow (Understand → Gather → Inform → Constraints → Options → Evaluate → Validate → Execute) with confidence scoring (high/medium/low), risk assessment, and escalation
- **Autonomy System**: 3 modes (Plan/Agent/Full Autonomous), 35+ capabilities with risk levels, 4-tier approval classes (None/Session/Project/Explicit), role-based permissions for all 7 agent roles, audit trail
- **Model Router**: Local-first LLM routing (Ollama) with cloud fallback (OpenAI/Anthropic)
- **MCP clients**: Firecrawl, GitHub, Agent Memory, MarkItDown
- **Tools layer**: FileTool, CommandTool, BrowserTool, GitTool, DatabaseTool, DockerTool with permission/risk validation
- **TOON serialization**: Recursive-descent TOON parser for compact internal memory representation
- **Database**: SQLAlchemy + SQLite with auto-seeding (all 8 agents created at startup)

### Frontend (Next.js 16)
- **5 pages**: Dashboard, Projects, Agents, Tasks, Memory
- **Live data**: API proxy forwards `/api/*` to backend at `localhost:8000`
- **Theme**: Dark industrial with amber accents
- **Stack**: TypeScript, Tailwind CSS, lucide-react

### Integration
- Frontend dev: `cd frontend && npm run dev` (port 3000)
- Backend dev: `cd backend && uvicorn backend.main:app --reload` (port 8000)
- API proxy configured in `frontend/next.config.ts`

### Workflow Engine
- **6 workflow types**: SDLC, Feature Development, Bug Fixing, Refactoring, Release, Task Pipeline
- **4 complexity tiers**: Simple → Moderate → Complex → Critical with escalating agent involvement
- **Step builders**: Each workflow generates correct step sequence (agents, gates, approvals) per classification
- **Task classifier**: Scores scope/risk/dependencies/architecture/security/research factors → complexity level
- **API endpoints**: POST /api/v1/workflows/blueprint, POST /api/v1/workflows/classify, GET /api/v1/workflows/categories

### Learning System
- **Failure Analysis**: Record/categorize failures with severity, root cause (5 Whys), preventive actions
- **Lessons Learned**: Create/search/promote/supersede lessons with evidence, confidence, and scope (project → project-type → global)
- **Performance Metrics**: Weighted scoring across 8 categories (correctness, quality, reliability, testing, research, learning, governance, efficiency) with warning/critical thresholds
- **Improvement Proposals**: Observation → evidence → benefit → risk → manager review → approve/reject
- **API**: Full CRUD for failures, lessons, metrics, proposals under /api/v1/learning/

### Weighted Memory Retrieval
- **7-factor scoring**: context match (25%), importance (18%), confidence (15%), outcome quality (15%), frequency (10%), relationship strength (10%), recency (7%)
- **8 agent profiles**: Manager, Architect, Planner, Coder, Tester, Debugger, Reviewer, Memory — each with weighted tag preferences
- **9 retrieval modes**: Planning, Architecture, Implementation, Testing, Debugging, Review, Learning, Research, Optimization
- **Knowledge Package**: Top-N memories, pattern summary, contradictions, knowledge graph, confidence score
- **Relationship expansion**: Auto-expand to related memories across the graph
- **Contradiction detection**: Opposite-direction keyword matching + tag overlap analysis
- **API**: Full retrieval, expansion, profiles under /api/v1/memory-retrieval/

### Next Priorities
- Frontend pages for new systems (learning dashboard, memory retrieval explorer, workflow builder)
- Integration testing across all subsystems
- Agent orchestration tests (Manager running workflows through agents)

---

## Guiding Philosophy

Read first.

Understand second.

Act third.

Every change should leave the system more understandable, more maintainable, and more capable than before.
