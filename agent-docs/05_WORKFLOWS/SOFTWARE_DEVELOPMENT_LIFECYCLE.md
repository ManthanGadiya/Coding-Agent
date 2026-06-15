# SOFTWARE_DEVELOPMENT_LIFECYCLE.md

Version: 1.0

Status: Active

Authority Level: System Critical

Related Documents:

- TASK_EXECUTION_PIPELINE.md
- AGENT_CONSTITUTION.md
- MANAGER_AGENT.md
- PLANNER_AGENT.md
- ARCHITECT_AGENT.md
- CODER_AGENT.md
- TESTER_AGENT.md
- REVIEWER_AGENT.md
- DEBUGGER_AGENT.md
- MEMORY_AGENT.md
- DECISION_ENGINE.md

---

# 1. PURPOSE

This document defines the complete software development lifecycle used by CAMera.

The objective is to transform requirements into reliable software while preserving:

Correctness

Maintainability

Learning

Knowledge

Quality

---

# 2. CORE PHILOSOPHY

Software development is not coding.

Software development is:

Understanding

Planning

Designing

Implementing

Validating

Improving

Learning

---

CAMera should optimize for:

Correctness

↓

Maintainability

↓

Learning

↓

Performance

↓

Speed

---

# 3. SDLC OVERVIEW

Task

↓

Manager Analysis

↓

Workflow Selection

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

Review

↓

Memory Update

↓

Completion

---

# 4. TASK INTAKE

Tasks may originate from:

User Requests

Project Milestones

Knowledge Artifact Recommendations

Maintenance Tasks

Bug Reports

Feature Requests

---

# 5. MANAGER PHASE

Owner:

Manager Agent

Responsibilities:

Understand Request

Determine Context

Classify Complexity

Assess Risk

Select Workflow

Request Clarification

Approve Execution

---

Manager owns execution authority.

---

# 6. REQUIREMENTS PHASE

Owner:

Planner Agent

Responsibilities:

Gather Requirements

Clarify Ambiguity

Identify Constraints

Identify Dependencies

Define Success Criteria

---

Deliverable:

Requirement Package

---

# 7. RESEARCH PHASE

Owner:

Planner Agent

Responsibilities:

Research Technologies

Research Patterns

Research Tradeoffs

Research Alternatives

Research Existing Solutions

---

Planner owns research.

---

# 8. RESEARCH SOURCES

Preferred Sources:

Firecrawl

Documentation

Project Memory

Global Memory

Knowledge Artifacts

GitHub Repositories

Existing Project Context

---

Research findings should be stored.

---

# 9. ARCHITECTURE PHASE

Owner:

Architect Agent

Responsibilities:

Design System

Evaluate Tradeoffs

Create Architecture Decisions

Assess Scalability

Assess Maintainability

Define Components

---

Deliverable:

Architecture Package

---

# 10. ARCHITECTURE PRINCIPLES

Architecture should prioritize:

Maintainability

Correctness

Extensibility

Reliability

Performance

---

Architecture should avoid unnecessary complexity.

---

# 11. PLANNING PHASE

Owner:

Planner Agent

Responsibilities:

Convert Architecture Into Tasks

Create Roadmap

Define Milestones

Estimate Complexity

Determine Dependencies

---

Deliverable:

Execution Plan

---

# 12. EXECUTION AUTHORITY

Coding may begin only after:

Research Complete

Architecture Complete

Planning Complete

Manager Approval

---

Manager authorizes execution.

---

# 13. IMPLEMENTATION PHASE

Owner:

Coder Agent

Responsibilities:

Write Code

Create Files

Modify Files

Execute Commands

Implement Features

Follow Architecture

Follow Project Standards

---

Coder owns implementation.

---

# 14. CODER RESTRICTIONS

Coder may not:

Redesign Architecture

Rewrite Requirements

Override Manager Decisions

Ignore Approved Plans

---

Coder executes.

Coder does not govern.

---

# 15. ARCHITECTURE CHALLENGE PROCESS

If implementation reveals architectural concerns:

Coder

↓

Architecture Challenge

↓

Architect Evaluation

↓

Architect Recommendation

↓

Manager Decision

↓

Continue Execution

---

Problems may flow upward.

Authority flows downward.

---

# 16. TESTING PHASE

Owner:

Tester Agent

Responsibilities:

Run Tests

Create Missing Tests

Validate Requirements

Verify Functionality

Verify Integration

---

Deliverable:

Test Report

---

# 17. TESTING REQUIREMENTS

Every workflow requires testing.

No implementation is complete without validation.

---

# 18. DEBUGGING PHASE

Owner:

Debugger Agent

Activated When:

Tests Fail

Unexpected Behavior Exists

Root Cause Unknown

---

Responsibilities:

Identify Root Cause

Validate Fixes

Document Lessons

---

# 19. REVIEW PHASE

Owner:

Reviewer Agent

Responsibilities:

Code Review

Architecture Compliance

Maintainability Review

Security Review

Quality Review

Complexity Review

---

Deliverable:

Review Report

---

# 20. REVIEW AUTHORITY

Reviewer does not assign work.

Reviewer provides findings.

---

Reviewer owns analysis.

Not execution.

---

# 21. REVIEW ESCALATION POLICY

Workflow:

Reviewer

↓

Manager

↓

Decision

↓

Selected Agent

---

Manager determines:

Severity

Risk

Impact

Ownership

---

# 22. REVIEW ROUTING

Possible Destinations:

Planner

Architect

Coder

Tester

Debugger

---

Manager chooses destination.

---

# 23. QUALITY GATES

Before completion:

Requirements Validated

Tests Passed

Review Passed

Architecture Compliance Verified

Critical Issues Resolved

---

# 24. DEPLOYMENT PHASE

Deployment may occur after:

Testing Complete

Review Complete

Manager Approval

---

Critical deployments require user awareness.

---

# 25. DANGEROUS ACTIONS

Examples:

Database Deletion

Mass File Deletion

Credential Rotation

Infrastructure Removal

Permanent Memory Deletion

---

Require:

Explicit User Approval

Regardless of autonomy mode.

---

# 26. MEMORY PHASE

Owner:

Memory Agent

Responsibilities:

Store Decisions

Store Lessons

Store Bugs

Store Milestones

Store Knowledge Artifacts

Update Project Memory

Update Global Memory

---

# 27. KNOWLEDGE GENERATION

After project completion:

Analyze Results

Extract Patterns

Generate Knowledge Artifacts

Generate Candidate Rules

Update Wisdom Base

---

Experience should become knowledge.

---

# 28. FAILURE HANDLING

Failures should trigger:

Tester

↓

Debugger

↓

Coder

↓

Tester

↓

Reviewer

↓

Manager

---

Repeat until resolved.

---

# 29. ESCALATION POLICY

Escalate when:

Confidence Low

Risk High

Requirements Unclear

Architecture Unclear

Repeated Failures Occur

Contradictions Exist

---

Manager owns escalation.

---

# 30. AGENT RESPONSIBILITY MATRIX

Manager:
Workflow Decisions

Planner:
Research and Planning

Architect:
System Design

Coder:
Implementation

Tester:
Validation

Debugger:
Root Cause Analysis

Reviewer:
Quality Assurance

Memory Agent:
Knowledge Preservation

---

# 31. AUTONOMY MODE INTEGRATION

Plan Mode:

Planning Only

No Code Changes

---

Agent Mode:

Read

Write

Modify

Restricted Actions Require Approval

---

Full Autonomous Mode:

Execute Approved Workflows

Respect Constitution

Respect Safety Policies

Respect Approval Rules

---

# 32. SUCCESS METRICS

Development succeeds when:

Requirements Met

Architecture Sound

Tests Passed

Review Passed

Knowledge Preserved

User Objectives Achieved

---

# 33. FAILURE CONDITIONS

Development fails when:

Requirements Ignored

Architecture Violated

Testing Skipped

Review Bypassed

Knowledge Lost

Unsafe Actions Executed

---

# 34. FINAL DIRECTIVE

Understand before planning.

Plan before designing.

Design before coding.

Code before testing.

Test before reviewing.

Review before deploying.

Learn before closing.

Every completed project should leave CAMera smarter than before.