# ESCALATION_POLICY.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

* DECISION_ENGINE.md
* PRIORITY_RULES.md
* CONFLICT_RESOLUTION.md
* COMPLETION_CRITERIA.md
* AGENT_TOPOLOGY.md

---

# 1. PURPOSE

This document defines when CAMera agents must escalate issues.

Escalation exists to:

* Reduce risk
* Improve decision quality
* Prevent deadlocks
* Protect system integrity

Escalation should occur only when necessary.

---

# 2. ESCALATION PHILOSOPHY

Agents should:

Solve locally first.

Escalate only when:

* Authority exceeded
* Confidence too low
* Risk too high
* Progress blocked

---

# 3. ESCALATION HIERARCHY

Level 1

Agent-to-Agent

---

Level 2

Agent-to-Manager

---

Level 3

Manager-to-User

---

Level 4

Emergency Escalation

---

Escalation should always use the lowest effective level.

---

# 4. AGENT-TO-AGENT ESCALATION

Use when:

Missing information

Need expertise

Need validation

Need clarification

Examples:

Coder → Planner

Tester → Debugger

Planner → Architect

Reviewer → Tester

---

# 5. AGENT-TO-MANAGER ESCALATION

Use when:

Consensus fails

Risk increases

Authority exceeded

Work becomes blocked

Requirements conflict

---

Manager becomes responsible for resolution.

---

# 6. MANAGER-TO-USER ESCALATION

Use when:

Strategic decision required

Tradeoffs significant

Approval required

Requirements unclear

User goals conflict

---

User retains final authority.

---

# 7. LOW CONFIDENCE ESCALATION

Confidence Levels

High

Medium

Low

---

If confidence is Low:

Agent must:

Research

Validate

Seek assistance

or

Escalate

---

Low-confidence execution is discouraged.

---

# 8. SECURITY ESCALATION

Immediate escalation required for:

Credential exposure

Secret leakage

Authentication failures

Authorization failures

Critical vulnerabilities

---

Flow:

Agent

↓

Manager

↓

User

---

# 9. PERFORMANCE ESCALATION

Escalate when:

Critical regressions detected

Benchmarks fail

Resource usage excessive

Scalability concerns emerge

---

Performance impact must be measured.

---

# 10. ARCHITECTURE ESCALATION

Escalate when:

Architecture becomes invalid

Requirements change significantly

Dependencies create risk

Scalability concerns emerge

---

Architect owns first response.

Manager owns final coordination.

---

# 11. REQUIREMENT ESCALATION

Escalate when:

Requirements conflict

Requirements unclear

Requirements impossible

Requirements incomplete

---

Planner owns clarification process.

---

# 12. TESTING ESCALATION

Escalate when:

Critical tests fail

Validation impossible

Coverage insufficient

Regression risk high

---

Tester initiates escalation.

---

# 13. DEBUGGING ESCALATION

Escalate when:

Root cause unknown

Fix repeatedly fails

System instability grows

Multiple failures interact

---

Debugger owns escalation.

---

# 14. REVIEW ESCALATION

Escalate when:

Security risks exist

Maintainability risks exist

Architecture violations exist

Constitution violations exist

---

Reviewer initiates escalation.

---

# 15. MEMORY ESCALATION

Escalate when:

Conflicting memories exist

Knowledge corruption exists

Memory retrieval fails

Critical knowledge lost

---

Memory Agent initiates escalation.

---

# 16. TOOL FAILURE ESCALATION

Escalate when:

Tool unavailable

Tool repeatedly fails

Tool returns invalid results

Tool creates risk

---

Flow:

Agent

↓

Alternative Tool

↓

Retry

↓

Manager Escalation

---

# 17. MCP FAILURE ESCALATION

Escalate when:

MCP unavailable

Authentication failure

Connection failure

Invalid responses

---

Attempt recovery first.

Escalate if unresolved.

---

# 18. GITHUB ESCALATION

Mandatory escalation for:

Push operations

Branch creation

Repository deletion

Force operations

Destructive repository changes

---

User approval required.

---

# 19. FILESYSTEM ESCALATION

Mandatory escalation for:

Large deletions

Project deletion

Critical file deletion

Destructive operations

---

Rollback point required.

---

# 20. DEADLOCK ESCALATION

Deadlock Conditions:

Repeated disagreement

No progress

Circular dependencies

Conflicting objectives

---

Flow:

Agents

↓

Manager

↓

Decision

or

User Escalation

---

# 21. EMERGENCY ESCALATION

Emergency Conditions:

Critical security issue

Critical architecture flaw

Data loss risk

Catastrophic failure

Constitution violation

---

Emergency Flow:

Discovering Agent

↓

Architect

↓

Manager

↓

Immediate Evaluation

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

# 22. PAUSE AUTHORITY

Manager may pause execution when:

Risk exceeds threshold

Requirements invalid

Architecture compromised

Security compromised

Constitution threatened

---

# 23. ESCALATION PACKAGE FORMAT

Every escalation must include:

Issue

Severity

Impact

Evidence

Recommendations

Confidence

Proposed Action

---

# 24. ESCALATION SEVERITY LEVELS

Level 1

Informational

---

Level 2

Warning

---

Level 3

Significant Risk

---

Level 4

Critical

---

Level 5

Emergency

---

Escalation urgency should match severity.

---

# 25. USER ESCALATION REPORT

Manager must provide:

Summary

Evidence

Options

Tradeoffs

Recommendation

Required Decision

---

User should never receive raw agent disagreements without context.

---

# 26. ESCALATION TRACEABILITY

Every escalation must record:

Origin

Reason

Evidence

Resolution

Outcome

Timestamp

Lessons Learned

---

# 27. ESCALATION LEARNING

Resolved escalations should generate:

Lessons

Patterns

Workflow improvements

Memory updates

Architecture improvements

---

# 28. ESCALATION ABUSE PREVENTION

Agents must not:

Escalate unnecessarily

Avoid responsibility

Transfer simple decisions

Create escalation loops

---

Escalation is a tool.

Not a shortcut.

---

# 29. FINAL ESCALATION DIRECTIVE

Solve locally when possible.

Escalate when necessary.

Protect system quality.

Protect user interests.

Protect constitutional integrity.

When uncertainty becomes dangerous:

Escalate.
