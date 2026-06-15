# TOOL_ARCHITECTURE.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

* AGENT_CONSTITUTION.md
* SYSTEM_ARCHITECTURE.md
* AGENT_TOPOLOGY.md
* MEMORY_ARCHITECTURE.md

---

# 1. PURPOSE

This document defines:

* Tool ownership
* Tool permissions
* Tool usage rules
* MCP usage rules
* Skill activation rules

Tools perform actions.

Agents make decisions.

---

# 2. TOOL PHILOSOPHY

CAMera follows:

Decision
↓
Tool Selection
↓
Execution
↓
Validation

Tools never make decisions.

Agents always remain responsible.

---

# 3. TOOL CATEGORIES

### Execution Tools

* Terminal
* Filesystem
* Docker

---

### Repository Tools

* GitHub MCP
* Git Tools

---

### Research Tools

* Firecrawl MCP
* MarkItDown MCP
* temp_websearch_skill
* agent-browser

---

### Memory Tools

* Agent Memory MCP

---

### Integration Tools

* Composio MCP

---

### Workflow Tools

* autoplan
* review
* investigate
* health
* benchmark

---

# 4. TOOL OWNERSHIP MATRIX

Manager

Can Use:

* All tools

Purpose:

System coordination.

---

Architect

Can Use:

* Firecrawl
* MarkItDown
* Memory

Cannot:

* Modify code directly

---

Planner

Can Use:

* Firecrawl
* MarkItDown
* agent-browser
* temp_websearch_skill
* Memory

Purpose:

Research and planning.

---

Coder

Can Use:

* Filesystem
* Terminal
* Git (local)
* Docker

Cannot Use Directly:

* Firecrawl
* MarkItDown
* Research tools

Must request research from Planner.

---

Tester

Can Use:

* Terminal
* Testing frameworks
* Benchmark
* Health

---

Debugger

Can Use:

* Terminal
* Logs
* Investigate Skill
* Benchmark
* Health

---

Reviewer

Can Use:

* Review Skill
* Health
* Benchmark

---

Memory Agent

Can Use:

* Agent Memory MCP

Exclusive Authority:

Memory management.

---

# 5. MCP ARCHITECTURE

## Agent Memory MCP

Owner:

Memory Agent

Purpose:

Knowledge persistence.

---

## Firecrawl MCP

Owner:

Planner

Secondary Access:

Architect

Purpose:

Documentation gathering.

---

## GitHub MCP

Owner:

Manager

Secondary Access:

Coder

Restrictions:

Push requires approval.

---

## MarkItDown MCP

Owner:

Planner

Secondary Access:

Architect

Purpose:

Document conversion.

---

## Composio MCP

Owner:

Manager

Purpose:

External service integration.

---

## Hermes Agent MCP

Owner:

Manager

Purpose:

Advanced orchestration.

---

## Ruflo MCP

Owner:

Manager

Purpose:

Workflow enhancement.

---

# 6. SKILL ACTIVATION RULES

## autoplan

Activate When:

Project complexity is high.

---

## investigate

Activate When:

Root cause is unknown.

---

## review

Activate Before:

Major completion.

---

## benchmark

Activate When:

Performance matters.

---

## health

Activate Before:

Release.

---

## design-review

Activate For:

UI changes.

---

## plan-eng-review

Activate For:

Architecture-sensitive plans.

---

## plan-ceo-review

Activate For:

Scope decisions.

---

## plan-devex-review

Activate For:

Developer experience evaluation.

---

## agent-browser

Activate For:

Website interaction.

---

## temp_websearch_skill

Activate For:

General research.

---

# 7. TERMINAL POLICY

Allowed:

* Build
* Test
* Lint
* Run
* Debug

Restricted:

* Destructive commands

Requires Confirmation:

* Mass deletion
* System-level modifications

---

# 8. FILESYSTEM POLICY

Allowed:

* Read
* Create
* Modify

Requires Confirmation:

* Delete
* Move critical files

---

# 9. GITHUB POLICY

Allowed:

* Read repositories
* Create local commits

Requires Approval:

* Push
* Branch creation
* Pull requests
* Repository deletion

---

# 10. RESEARCH POLICY

Research ownership belongs to Planner.

Research workflow:

Need Identified
↓
Planner
↓
Research Tools
↓
Knowledge Package
↓
Requesting Agent

No other agent performs independent research unless authorized.

---

# 11. TOOL FAILURE POLICY

Tool Failure
↓
Agent Detects
↓
Alternative Tool Search
↓
Retry
↓
Escalation

Failure must be logged.

---

# 12. SECURITY POLICY

Tools must never:

* Expose secrets
* Leak credentials
* Execute unsafe actions
* Ignore confirmation requirements

---

# 13. AUDITABILITY POLICY

Every tool action must record:

Tool

Agent

Reason

Timestamp

Result

Outcome

---

# 14. AUTONOMY POLICY

Higher autonomy requires:

Higher verification.

Tool power must scale with confidence.

---

# 15. FINAL TOOL DIRECTIVE

Agents think.

Tools act.

Research belongs to Planner.

Memory belongs to Memory Agent.

Coordination belongs to Manager.

No tool may bypass constitutional authority.
