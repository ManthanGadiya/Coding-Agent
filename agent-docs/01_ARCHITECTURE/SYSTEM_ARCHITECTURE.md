# SYSTEM_ARCHITECTURE.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

* AGENT_CONSTITUTION.md
* PROJECT_VISION.md
* DESIGN_PRINCIPLES.md
* SUCCESS_CRITERIA.md

---

# 1. PURPOSE

This document defines the overall architecture of CAMera.

It describes:

* Major components
* Responsibilities
* Communication flows
* System boundaries
* Data movement
* Decision hierarchy

Every future implementation must conform to this architecture.

---

# 2. SYSTEM OVERVIEW

CAMera is a Hybrid Autonomous Software Engineering System.

Architecture Type:

Hybrid Multi-Agent System

Core Components:

1. User Layer
2. Manager Layer
3. Agent Layer
4. Memory Layer
5. Tool Layer
6. MCP Layer
7. Model Layer
8. Infrastructure Layer

---

# 3. HIGH LEVEL ARCHITECTURE

User
↓
Manager Agent
↓
Architect Agent
↓
Planner Agent
↓
Coder Agent
↓
Tester Agent
↓
Debugger Agent
↓
Reviewer Agent
↓
Memory Agent

All Agents
↓
Tools
↓
MCPs
↓
Models

---

# 4. USER LAYER

Purpose:

Human interaction.

Responsibilities:

* Provide goals
* Approve critical actions
* Review tradeoffs
* Make final decisions

Authority:

Second highest authority after Constitution.

---

# 5. MANAGER LAYER

Purpose:

Project orchestration.

Responsibilities:

* Receive user goals
* Coordinate agents
* Resolve conflicts
* Track progress
* Determine completion

Inputs:

* User goals
* Agent outputs
* Memory

Outputs:

* Tasks
* Decisions
* Recommendations

Authority:

Highest operational authority.

---

# 6. AGENT LAYER

CAMera consists of specialized agents.

---

## Architect Agent

Purpose:

Design systems.

Responsibilities:

* Architecture design
* Technology selection
* Scalability evaluation
* Dependency evaluation

---

## Planner Agent

Purpose:

Research and planning.

Responsibilities:

* Requirement analysis
* Documentation research
* Risk analysis
* Task decomposition
* Roadmap creation

Planner owns research.

---

## Coder Agent

Purpose:

Implementation.

Responsibilities:

* Write code
* Refactor code
* Create integrations
* Generate documentation

---

## Tester Agent

Purpose:

Validation.

Responsibilities:

* Unit testing
* Integration testing
* Regression testing

---

## Debugger Agent

Purpose:

Failure investigation.

Responsibilities:

* Root cause analysis
* Error diagnosis
* Recovery recommendations

---

## Reviewer Agent

Purpose:

Quality assurance.

Responsibilities:

* Code review
* Architecture review
* Security review

---

## Memory Agent

Purpose:

Knowledge preservation.

Responsibilities:

* Memory storage
* Memory retrieval
* Knowledge organization

---

# 7. MEMORY LAYER

Memory Types:

---

## Global Memory

Stores:

* User preferences
* Communication preferences
* Learning preferences
* Long-term goals

Scope:

Cross-project.

---

## Project Memory

Stores:

* Requirements
* Architecture decisions
* Risks
* Lessons learned
* Project history

Scope:

Project specific.

---

# 8. TOOL LAYER

Tools extend capabilities.

Examples:

* Terminal
* Filesystem
* Browser
* Git
* Database
* Docker

Tools perform actions.

Agents make decisions.

---

# 9. MCP LAYER

MCPs provide specialized capabilities.

---

## Agent Memory MCP

Purpose:

Persistent knowledge.

---

## Firecrawl MCP

Purpose:

Research and documentation extraction.

---

## GitHub MCP

Purpose:

Repository management.

---

## MarkItDown MCP

Purpose:

Document conversion.

---

## Composio MCP

Purpose:

External integrations.

---

## Hermes Agent MCP

Purpose:

Advanced orchestration.

---

## Ruflo MCP

Purpose:

Workflow support.

---

# 10. SKILL LAYER

Skills provide reusable workflows.

Installed Skills Include:

* autoplan
* investigate
* review
* benchmark
* health
* design-review
* plan-eng-review
* plan-ceo-review
* plan-devex-review
* agent-browser
* temp_websearch_skill

Skills are activated when task conditions match their specialization.

---

# 11. MODEL LAYER

Purpose:

Reasoning and generation.

Supported Models:

Local Models:

* Qwen
* DeepSeek
* Future Local Models

Remote Models:

* OpenAI
* Anthropic
* Gemini
* Future Providers

Model routing determined by future Model Router.

Default Preference:

Local First.

Remote When Justified.

---

# 12. INFRASTRUCTURE LAYER

Components:

Frontend
Backend
Database
Vector Store
Local Models
Remote Models

Responsibilities:

Execution and persistence.

---

# 13. COMMUNICATION FLOW

User
↓
Manager

Manager
↓
Architect

Architect
↓
Planner

Planner
↓
Coder

Coder
↓
Tester

Tester
↓
Debugger (if failure)

Debugger
↓
Coder

Tester
↓
Reviewer

Reviewer
↓
Manager

Manager
↓
User

---

# 14. MEMORY FLOW

Event Occurs
↓
Manager Evaluates Importance
↓
Memory Agent
↓
Global Memory OR Project Memory
↓
Future Retrieval

---

# 15. TASK EXECUTION FLOW

Goal Received
↓
Research
↓
Architecture
↓
Planning
↓
Implementation
↓
Testing
↓
Debugging
↓
Review
↓
Memory Update
↓
Completion

---

# 16. AUTONOMY ARCHITECTURE

Planning Mode:

Research and planning only.

---

Agent Mode:

Read
Modify
Execute

Within permissions.

---

Full Autonomous Mode:

Plan
Build
Test
Debug
Review

Subject to constitutional constraints.

---

# 17. FAILURE RECOVERY FLOW

Failure Detected
↓
Tester
↓
Debugger
↓
Root Cause Analysis
↓
Fix Proposal
↓
Validation
↓
Review
↓
Continue

---

# 18. SCALABILITY STRATEGY

Phase 1:

Single User
Single Project

---

Phase 2:

Single User
Multiple Projects

---

Phase 3:

Advanced Multi-Agent Coordination

---

Phase 4:

Self-Improving Engineering Platform

---

# 19. ARCHITECTURAL RULES

No component may bypass:

* Constitution
* Manager Agent
* Memory Layer

All significant decisions must be traceable.

All important knowledge must be preservable.

---

# 20. FINAL ARCHITECTURE DIRECTIVE

CAMera shall operate as a coordinated engineering system rather than a standalone language model.

Agents think.

Tools act.

Memory remembers.

Manager coordinates.

User decides.

Constitution governs.
