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
- **52 API routes** across projects, tasks, agents, memory, workflows, and LLM
- **7 agents**: Orchestrator, Coder, Reviewer, Tester, Memory, Debugger (+ LLM-based Architect & Planner planned)
- **Model Router**: Local-first LLM routing (Ollama) with cloud fallback (OpenAI/Anthropic)
- **MCP clients**: Firecrawl, GitHub, Agent Memory, MarkItDown
- **Tools layer**: FileTool, CommandTool with permission validation

### Frontend (Next.js 16)
- **5 pages**: Dashboard, Projects, Agents, Tasks, Memory
- **Live data**: API proxy forwards `/api/*` to backend at `localhost:8000`
- **Theme**: Dark industrial with amber accents
- **Stack**: TypeScript, Tailwind CSS, lucide-react

### Integration
- Frontend dev: `cd frontend && npm run dev` (port 3000)
- Backend dev: `cd backend && uvicorn backend.main:app --reload` (port 8000)
- API proxy configured in `frontend/next.config.ts`

### Next Priorities
- Convert static pages to live data-fetching components
- Architect & Planner agent implementations
- MCP server implementations for external services
- TOON memory serialization
- Learning system (failure analysis, lessons)

---

## Guiding Philosophy

Read first.

Understand second.

Act third.

Every change should leave the system more understandable, more maintainable, and more capable than before.
