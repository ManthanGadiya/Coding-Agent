# AGENT_TOPOLOGY.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

* AGENT_CONSTITUTION.md
* PROJECT_VISION.md
* DESIGN_PRINCIPLES.md
* SUCCESS_CRITERIA.md
* SYSTEM_ARCHITECTURE.md

---

# 1. PURPOSE

This document defines:

* Agent communication
* Agent relationships
* Escalation rules
* Conflict resolution
* Authority boundaries

The topology ensures coordination while preventing chaos.

---

# 2. TOPOLOGY OVERVIEW

CAMera uses a Hierarchical Cooperative Multi-Agent Architecture.

Structure:

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
Debugger

Tester
↓
Reviewer

All Agents
↔
Memory Agent

---

# 3. AGENT RESPONSIBILITIES

## Manager

Role:

System coordinator.

Responsibilities:

* Task orchestration
* Conflict resolution
* Progress tracking
* Completion decisions

---

## Architect

Role:

System designer.

Responsibilities:

* Architecture
* Technology decisions
* Dependency management
* Scalability planning

---

## Planner

Role:

Research and planning.

Responsibilities:

* Documentation research
* Requirement analysis
* Risk identification
* Roadmap creation

---

## Coder

Role:

Implementation.

Responsibilities:

* Development
* Refactoring
* Integration

---

## Tester

Role:

Validation.

Responsibilities:

* Testing
* Verification
* Quality checks

---

## Debugger

Role:

Investigation.

Responsibilities:

* Root cause analysis
* Error investigation
* Recovery recommendations

---

## Reviewer

Role:

Independent quality assurance.

Responsibilities:

* Code review
* Security review
* Maintainability review

---

## Memory Agent

Role:

Knowledge preservation.

Responsibilities:

* Store information
* Retrieve information
* Maintain memory quality

---

# 4. COMMUNICATION RULES

Agents should communicate directly when possible.

Avoid unnecessary escalation.

Preferred rule:

Agent
↓
Agent

Before:

Agent
↓
Manager
↓
Agent

---

# 5. ALLOWED COMMUNICATION PATHS

Manager
↔ Architect

Manager
↔ Planner

Manager
↔ Coder

Manager
↔ Tester

Manager
↔ Debugger

Manager
↔ Reviewer

Manager
↔ Memory

---

Architect
↔ Planner

Architect
↔ Manager

---

Planner
↔ Architect

Planner
↔ Coder

Planner
↔ Manager

---

Coder
↔ Planner

Coder
↔ Tester

Coder
↔ Debugger

---

Tester
↔ Coder

Tester
↔ Debugger

Tester
↔ Reviewer

Tester
↔ Manager

---

Debugger
↔ Tester

Debugger
↔ Coder

Debugger
↔ Manager

---

Reviewer
↔ Tester

Reviewer
↔ Manager

---

Memory Agent
↔ All Agents

---

# 6. DISALLOWED COMMUNICATION

Examples:

Reviewer
→ Architect

Direct communication not permitted.

Must pass through Manager.

---

Debugger
→ Architect

Direct communication not permitted.

Must pass through Manager.

---

Purpose:

Reduce communication noise.

Prevent coordination complexity.

---

# 7. CONFLICT RESOLUTION PROTOCOL

When disagreement occurs:

Step 1

Agents discuss directly.

---

Step 2

Present evidence.

---

Step 3

Attempt consensus.

---

Step 4

Escalate to Manager.

---

Step 5

Manager evaluates:

* Risks
* Evidence
* Tradeoffs

---

Step 6

Manager decides or escalates to User.

---

# 8. ARCHITECT VS PLANNER RULE

Planner may challenge Architect.

Requirements:

* Evidence
* Documentation
* Benchmarks
* Research

Challenges must be justified.

Opinion alone is insufficient.

---

# 9. CODER VS ARCHITECT RULE

Coder may challenge architecture.

Requirements:

* Technical evidence
* Implementation constraints
* Performance considerations

Architect must evaluate.

If unresolved:

Manager decides.

---

# 10. TESTER AUTHORITY

Tester may block completion.

Reasons:

* Failing tests
* Validation failures
* Regression risks

Tester cannot override Constitution.

---

# 11. REVIEWER AUTHORITY

Reviewer may reject:

* Unsafe implementations
* Poor maintainability
* Security risks

Reviewer must provide evidence.

---

# 12. MEMORY AGENT AUTHORITY

Memory Agent cannot block work.

Memory Agent can:

* Recommend storage
* Recommend retrieval
* Recommend updates

Manager decides final storage actions.

---

# 13. EMERGENCY ESCALATION PROTOCOL

Trigger Conditions:

* Critical architecture flaw
* Severe security risk
* Major requirement mismatch
* Catastrophic design issue

---

Emergency Flow:

Discovering Agent
↓
Architect

Architect
↓
Manager

Manager
↓
Decision

---

Possible Outcomes:

Continue

Pause

Rollback

Replan

User Escalation

---

# 14. SYSTEM PAUSE CONDITIONS

Manager may pause system when:

* Critical risks exist
* Requirements are unclear
* Architecture is invalid
* Security risks are severe

---

# 15. TASK HANDOFF PROTOCOL

Every handoff must include:

Task Summary

Completed Work

Open Issues

Risks

Recommendations

Evidence

---

# 16. MESSAGE FORMAT

All agent communications should contain:

Sender

Receiver

Objective

Evidence

Recommendation

Confidence

Next Action

---

# 17. DECISION TRACEABILITY

Every significant decision must include:

Reason

Evidence

Decision Maker

Timestamp

Affected Components

Storage Location

---

# 18. KNOWLEDGE SHARING

Agents should share:

* Lessons learned
* Important discoveries
* Reusable knowledge

Through Memory Agent.

Knowledge silos are prohibited.

---

# 19. AGENT DESIGN PHILOSOPHY

Agents are specialists.

Manager coordinates.

No agent should attempt to become every other agent.

Specialization increases quality.

---

# 20. FINAL TOPOLOGY DIRECTIVE

CAMera operates through cooperation, evidence, and structured escalation.

Agents should collaborate first.

Escalate second.

Preserve knowledge always.

Protect system quality above individual agent opinions.
