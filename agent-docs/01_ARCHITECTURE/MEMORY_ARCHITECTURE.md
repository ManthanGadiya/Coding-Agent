# MEMORY_ARCHITECTURE.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

* AGENT_CONSTITUTION.md
* PROJECT_VISION.md
* SUCCESS_CRITERIA.md
* DATA_FLOW.md
* SYSTEM_ARCHITECTURE.md

---

# 1. PURPOSE

This document defines the complete memory system of CAMera.

Objectives:

* Preserve knowledge
* Reduce repeated work
* Improve future decisions
* Improve planning quality
* Improve teaching quality
* Improve software quality

Memory exists to make future work better.

---

# 2. MEMORY PHILOSOPHY

Knowledge should not be lost.

However:

Not all information deserves memory.

Memory should contain:

High-value knowledge.

Not:

Complete history.

CAMera must remember what matters.

Forget what does not.

---

# 3. MEMORY TYPES

CAMera contains two primary memory systems.

Global Memory

Project Memory

---

# 4. GLOBAL MEMORY

Purpose:

Cross-project knowledge.

Scope:

All projects.

Persistence:

Permanent until removed.

---

Store:

User Preferences

Communication Style

Learning Preferences

Coding Preferences

Framework Preferences

Technology Preferences

Long-Term Goals

Recurring Mistakes

Successful Patterns

Engineering Philosophy

Preferred Workflows

---

Examples:

User prefers FastAPI.

User learns visually.

User prefers maintainability.

User dislikes hidden complexity.

---

# 5. PROJECT MEMORY

Purpose:

Project-specific knowledge.

Scope:

Current project only.

Persistence:

Until project archival.

---

Store:

Requirements

Architecture Decisions

Technology Choices

Risks

Lessons Learned

Bugs

Workarounds

Design Decisions

Project Constraints

Deployment Information

---

Examples:

Project uses PostgreSQL.

JWT chosen over sessions.

Redis introduced for caching.

---

# 6. MEMORY OWNERSHIP

Memory Agent owns:

Storage

Retrieval

Compression

Classification

Deduplication

Validation

All other agents may:

Read

Request Storage

Request Updates

---

# 7. MEMORY CATEGORIES

Every memory entry must belong to a category.

Categories:

Preference

Knowledge

Decision

Lesson

Mistake

Risk

Constraint

Workflow

Architecture

Technology

Bug

Improvement

---

# 8. MEMORY SCORING SYSTEM

Every memory receives a score.

Criteria:

Importance

Reusability

Frequency

Impact

Longevity

---

Low Score:

Discard

---

Medium Score:

Store Temporarily

---

High Score:

Store Permanently

---

# 9. STORAGE RULES

Always Store:

Architecture Decisions

Major Lessons

User Preferences

Recurring Problems

Successful Workflows

Technology Decisions

Critical Bugs

Security Discoveries

---

Never Automatically Store:

Temporary Searches

Random Documentation

Duplicate Information

Trivial Facts

Low-Value Results

---

# 10. MEMORY CREATION FLOW

Event Occurs

↓

Agent Identifies Knowledge

↓

Memory Candidate Created

↓

Memory Agent Evaluates

↓

Score Assigned

↓

Store or Discard

---

# 11. MEMORY RETRIEVAL FLOW

Task Starts

↓

Manager Requests Context

↓

Memory Agent Searches

↓

Relevant Memories Retrieved

↓

Context Package Generated

↓

Delivered To Agent

---

# 12. MEMORY UPDATE FLOW

Existing Memory Found

↓

New Information Arrives

↓

Compare

↓

Update

Merge

Replace

Ignore

↓

Store Revised Version

---

# 13. MEMORY DEDUPLICATION

Duplicate knowledge should be avoided.

If similar memory exists:

Update Existing Entry

Do Not Create Duplicate

---

# 14. MEMORY COMPRESSION

Older memories may be compressed.

Compression Goals:

Reduce storage

Reduce retrieval noise

Preserve important information

---

Example:

50 bug reports

↓

Common patterns

↓

Single lesson learned

---

# 15. MEMORY RETENTION POLICY

Global Memory:

Retain indefinitely.

Unless explicitly removed.

---

Project Memory:

Retain while project active.

Archive after completion.

---

# 16. KNOWLEDGE EVALUATION RULE

Research does NOT automatically become memory.

Research must pass evaluation.

Questions:

Will this matter later?

Can this help future projects?

Will this improve decisions?

Will this reduce future work?

If no:

Do not store.

---

# 17. MEMORY QUALITY RULES

Memory must be:

Accurate

Relevant

Actionable

Non-duplicative

Traceable

---

Low-quality memory should be removed.

---

# 18. MEMORY AUDIT SYSTEM

Periodic audits should:

Remove duplicates

Remove obsolete information

Merge similar memories

Update outdated knowledge

---

# 19. MEMORY FAILURE HANDLING

If memory becomes:

Corrupted

Conflicting

Outdated

Incomplete

Memory Agent must:

Flag issue

Request review

Repair records

---

# 20. MEMORY ACCESS CONTROL

All agents may read memory.

Only Memory Agent may:

Approve Storage

Delete Memory

Compress Memory

Archive Memory

---

# 21. MEMORY PRIORITY

Highest Priority:

User Preferences

Architecture Decisions

Project Constraints

Critical Lessons

Critical Bugs

---

Medium Priority:

Workflow Optimizations

Technology Comparisons

Performance Findings

---

Low Priority:

Temporary Discoveries

One-Time Searches

Short-Lived Information

---

# 22. MEMORY AS LEARNING SYSTEM

The purpose of memory is not storage.

The purpose of memory is improvement.

Every memory should help:

Future Planning

Future Architecture

Future Development

Future Teaching

Future Decision Making

---

# 23. FUTURE MEMORY EVOLUTION

Phase 1

Simple structured memory.

---

Phase 2

Vector retrieval.

---

Phase 3

Memory relationships.

---

Phase 4

Knowledge graph.

---

Phase 5

Self-organizing memory network.

---
# 25. Memory Serialization Standard
All internal memory records should use TOON.

Reasons:

- Lower token usage
- Better context density
- Easier compression
- Better memory retrieval

Exceptions:

- MCP communication
- External APIs
- Third-party integrations


# 26. FINAL MEMORY DIRECTIVE

Remember what matters.

Forget what does not.

Preserve knowledge.

Reduce repetition.

Improve future decisions.

Make every project benefit from every previous project.
