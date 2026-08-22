CAMera: Phase 2 Plan — From Architecture to Runtime
Current State
Layer	What Exists	What's Missing
Agent Runtime	8 agent classes with process_task stubs	No automatic orchestration pipeline. CoderAgent._implement() returns a string literal, doesn't use LLM
Manager Runtime	Classify, route, assign, resolve, monitor methods	No run_goal() that takes "build X" and orchestrates Planner→Architect→Coder→Tester→Reviewer automatically
Model Router	3 providers (Ollama, OpenAI, Anthropic), selects by complexity	No per-agent routing (DeepSeek→coder, Claude→architecture), no cost/latency weighting
Memory Engine	Read/write, compress, retrieve, retention, knowledge APIs	None of it runs automatically. MemoryAgent returns stubs. Pipeline doesn't inject memory into agent prompts
SDLC Execution	Workflow blueprints + pipeline state machine defined	No way to go from "user says implement X" → autonomous multi-agent pipeline
Frontend	7 real pages, 2 stubs (/memory, /tasks)	Stubs have hardcoded data, no API calls
Plan (5 phases, ordered by dependency)
Phase 1: Manager Runtime (the backbone)
- Add run_goal(goal: str) -> Dict to ManagerAgent that:
1. Classifies + assesses complexity
2. Selects + instantiates a pipeline
3. Calls Planner → Architect (if complex) → Coder → Tester → Reviewer sequentially
4. Passes structured outputs between agents
5. Stores to memory, returns result
- API endpoint: POST /agents/run-goal
Phase 2: LLM-powered Agents (make agents think)
- Wire ModelRouter into every agent's process_task()
- Agent system prompts per role (architecture/planning/coding/testing/reviewing)
- CoderAgent: replaces _implement() stub with proper LLM prompt → file write flow
- PlannerAgent: research + planning via LLM
- ReviewerAgent: actual code review via LLM
Phase 3: Model Router Intelligence
- Multi-factor routing: score = w1*cost + w2*latency + w3*quality + w4*privacy
- Per-agent model suggestions: Planner→Gemini (research), Architect→Claude (architecture), Coder→DeepSeek (coding), Tester→local (cost)
- Fallback chain: cloud → local_large → local_medium → local_small
Phase 4: Memory Pipeline (automatic)
- MemoryAgent receives every agent's output automatically
- Auto-store decisions, lessons, artifacts after each pipeline step
- Auto-compress after N new entries
- Auto-score/retention check on each write
Phase 5: Frontend wiring
- /memory page: replace hardcoded data with real API calls to /api/memory/
- /tasks page: replace hardcoded data with real API calls to /api/tasks/
- Add goal input to dashboard for POST /agents/run-goal