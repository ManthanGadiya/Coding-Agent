# TASK_EXECUTION_PIPELINE.md

Version: 1.0

Status: Active

Authority Level: System Critical

Related Documents:

- AGENT_CONSTITUTION.md
- DECISION_ENGINE.md
- AUTONOMY_MODES.md
- MANAGER_AGENT.md
- PLANNER_AGENT.md
- ARCHITECT_AGENT.md
- CODER_AGENT.md
- TESTER_AGENT.md
- REVIEWER_AGENT.md
- MEMORY_AGENT.md

---

# 1. PURPOSE

This document defines the default execution pipeline for all tasks inside CAMera.

Every task must pass through this pipeline before execution.

The objective is:

Use the simplest workflow capable of safely solving the task.

Avoid:

Over-Engineering

Under-Engineering

Unnecessary Agent Activation

Wasted Resources

---

# 2. CORE PHILOSOPHY

Not every task requires every agent.

The workflow should adapt to:

Complexity

Risk

Impact

Uncertainty

The simplest workflow capable of safely solving the task should always be selected.

---

# 3. PIPELINE OVERVIEW

Task Received

↓

Manager Analysis

↓

Complexity Classification

↓

Workflow Selection

↓

User Confirmation (if required)

↓

Execution

↓

Validation

↓

Memory Update

↓

Completion

---

# 4. TASK INTAKE

Tasks may originate from:

User Request

Workflow Trigger

Agent Recommendation

Knowledge Artifact Recommendation

System Maintenance

Project Milestone

---

# 5. MANAGER RESPONSIBILITIES

The Manager must:

Understand Task

Analyze Context

Assess Risk

Assess Complexity

Select Workflow

Determine Required Agents

Request Clarification When Necessary

---

# 6. COMPLEXITY CLASSIFICATION

Every task must be classified.

Possible Levels:

Simple

Moderate

Complex

Critical

---

# 7. SIMPLE TASKS

Examples:

Rename Variable

Update README

Fix Typo

Change Button Color

Small Bug Fix

Update Configuration

---

Characteristics:

Low Risk

Low Impact

Minimal Dependencies

Clear Requirements

---

# 8. MODERATE TASKS

Examples:

New API Endpoint

Dashboard Page

Database Migration

Authentication Page

Medium Bug Fix

---

Characteristics:

Some Dependencies

Moderate Impact

Limited Architecture Impact

---

# 9. COMPLEX TASKS

Examples:

Authentication System

Agent Memory System

Payment Integration

Multi-Agent Coordination

Major Refactor

---

Characteristics:

Cross-System Impact

Architecture Decisions Required

Significant Planning Required

Multiple Components Affected

---

# 10. CRITICAL TASKS

Examples:

Security Systems

Production Deployments

Database Rewrite

Infrastructure Migration

Agent Core Redesign

---

Characteristics:

High Risk

High Impact

System Stability Risk

Security Implications

---

# 11. COMPLEXITY ASSESSMENT FACTORS

Evaluate:

Scope

Risk

Dependencies

Architecture Impact

Security Impact

Performance Impact

Uncertainty

Required Research

---

# 12. WORKFLOW SELECTION RULE

The Manager shall select:

The smallest workflow capable of safely completing the task.

---

# 13. SIMPLE WORKFLOW

Manager

↓

Coder

↓

Tester

↓

Memory

---

Use when:

Requirements are clear.

Risk is low.

Architecture unchanged.

---

# 14. MODERATE WORKFLOW

Manager

↓

Planner

↓

Coder

↓

Tester

↓

Reviewer

↓

Memory

---

Use when:

Planning required.

Architecture mostly unchanged.

Moderate complexity exists.

---

# 15. COMPLEX WORKFLOW

Manager

↓

Planner

↓

Architect

↓

Planner

↓

Coder

↓

Tester

↓

Reviewer

↓

Memory

---

Use when:

Architecture decisions required.

Multiple systems affected.

Research required.

Long-term implications exist.

---

# 16. CRITICAL WORKFLOW

Manager

↓

Planner

↓

Architect

↓

Planner

↓

Coder

↓

Tester

↓

Debugger (if needed)

↓

Reviewer

↓

Manager Review

↓

Memory

---

Use when:

Failure cost is high.

Security involved.

Infrastructure involved.

Major risk exists.

---

# 17. USER CLARIFICATION RULE

Before workflow selection:

Manager must determine:

Confidence Level

Requirement Clarity

Task Ambiguity

---

# 18. CLARIFICATION TRIGGERS

Ask the user when:

Requirements ambiguous

Multiple interpretations exist

Business rules unknown

Architecture constraints unknown

Success criteria unclear

---

# 19. QUESTION GENERATION RULE

Questions should:

Reduce uncertainty

Reduce risk

Reduce rework

Improve planning quality

---

Avoid unnecessary questions.

---

# 20. COMPLEX TASK NOTIFICATION

When a task is classified as Complex:

Manager should inform the user.

Example:

Task Classification:
Complex

Recommended Workflow:

Planner
↓
Architect
↓
Planner
↓
Coder
↓
Tester
↓
Reviewer

Reason:
Architecture impact detected.

Proceed?

---

# 21. CRITICAL TASK NOTIFICATION

Critical tasks require:

User Awareness

Risk Explanation

Workflow Explanation

Approval

---

# 22. WORKFLOW REPORT

Workflow reports should include:

Complexity

Risk

Workflow

Participating Agents

Estimated Effort

Reasoning

---

# 23. AGENT ACTIVATION POLICY

Agents should activate only when required.

Avoid:

Unnecessary Planning

Unnecessary Architecture Reviews

Unnecessary Research

---

Efficiency matters.

---

# 24. RESEARCH REQUEST POLICY

If information is missing:

Coder

↓

Planner

↓

Research

↓

Knowledge Package

↓

Coder

---

Research belongs to Planner.

---

# 25. ARCHITECTURE REQUEST POLICY

If architecture decisions required:

Planner

↓

Architect

↓

Planner

↓

Execution

---

Architecture belongs to Architect.

---

# 26. VALIDATION POLICY

Every workflow must include validation.

Minimum:

Tester

---

Complex systems additionally require:

Reviewer

---

# 27. MEMORY UPDATE POLICY

Every completed workflow should update memory.

Possible Updates:

Decision Records

Lessons Learned

Bug Records

Knowledge Artifacts

Project Memory

Global Memory

---

# 28. FAILURE HANDLING

When failures occur:

Tester Detects

↓

Debugger Investigates

↓

Coder Fixes

↓

Tester Validates

↓

Reviewer Confirms

---

# 29. ESCALATION POLICY

Escalate when:

Confidence low

Risk high

Architecture unclear

Repeated failures occur

Contradictions unresolved

---

Manager owns escalation.

---

# 30. AUTONOMY MODE INTEGRATION

Execution behavior depends on Autonomy Mode.

Plan Mode:

Planning only.

No implementation.

---

Agent Mode:

May modify project.

Restricted actions require approval.

---

Full Autonomous Mode:

May execute approved workflows automatically.

Still respects Constitution.

---

# 31. KNOWLEDGE ARTIFACT INTEGRATION

Knowledge Artifacts may:

Recommend workflows

Recommend planning patterns

Recommend engineering practices

---

Knowledge Artifacts never override the user.

---

# 32. SUCCESS CRITERIA

Pipeline succeeds when:

Correct workflow selected

Risk reduced

Agent usage optimized

Task completed successfully

Knowledge preserved

---

# 33. FAILURE CONDITIONS

Pipeline fails when:

Wrong workflow selected

Unnecessary complexity introduced

Required agents skipped

User intent misunderstood

Knowledge lost

---

# 34. FINAL DIRECTIVE

Every task begins with understanding.

Classify before acting.

Plan before building.

Build before validating.

Validate before completing.

Learn before forgetting.

The correct workflow is the smallest workflow capable of safely delivering success.