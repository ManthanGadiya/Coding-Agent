# GLOBAL_MEMORY_SCHEMA.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

* MEMORY_ARCHITECTURE.md
* MEMORY_AGENT.md
* AGENT_CONSTITUTION.md
* DATA_FLOW.md

---

# 1. PURPOSE

This document defines the structure of Global Memory.

Global Memory stores cross-project knowledge.

The purpose of Global Memory is to preserve information that remains useful across multiple projects and over long periods of time.

Global Memory should improve future decisions.

---

# 2. GLOBAL MEMORY PHILOSOPHY

Store:

Knowledge

Preferences

Patterns

Lessons

Decisions

Constraints

Goals

Workflows

---

Do Not Store:

Temporary information

Session-specific information

Low-value observations

Short-lived discoveries

Duplicate knowledge

---

# 3. GLOBAL MEMORY CATEGORIES

Category Types:

User Preference

Learning Preference

Engineering Preference

Technology Preference

Architecture Preference

Long-Term Goal

Workflow Pattern

Decision Pattern

Risk Pattern

Lesson Learned

Success Pattern

Failure Pattern

Tool Preference

MCP Preference

Skill Preference

---

Every memory must belong to at least one category.

---

# 4. MEMORY RECORD STRUCTURE

Every memory entry must contain similiar to this toon format:

memory:
 id: MEM-001

 category:
  TechnologyPreference

 title:
  FastAPI Preferred

 context:
  AI Systems
  Agent Systems

 evidence:
  Project History

 confidence:
  0.95

 source:
  User Statement
---

# 5. MEMORY ID

Requirements:

Globally Unique

Immutable

Human Traceable

Examples:

MEM-000001

MEM-000002

MEM-000003

---

# 6. TITLE

Purpose:

Human-readable summary.

Examples:

User Prefers FastAPI

User Learns Visually

Maintainability Preferred Over Speed

---

# 7. CONTENT

Purpose:

Core memory information.

Examples:

FastAPI preferred for AI and Agent Systems.

Visual examples improve understanding.

Maintainability should generally outrank development speed.

---

# 8. CONTEXT

Purpose:

Explain when the memory applies.

Examples:

AI Projects

Web APIs

Agent Systems

Learning Sessions

Architecture Decisions

---

Context prevents incorrect usage.

---

# 9. EVIDENCE

Purpose:

Justify why memory exists.

Examples:

Repeated project usage

Explicit user statement

Successful implementation history

Measured performance improvements

Observed behavior

---

Memory without evidence should receive lower confidence.

---

# 10. CONFIDENCE SCORE

Range:

0.0 – 1.0

Examples:

1.00 = Explicitly confirmed

0.95 = Strong evidence

0.75 = Good evidence

0.50 = Weak evidence

0.25 = Uncertain

---

Confidence influences retrieval ranking.

---

# 11. SOURCE

Possible Sources:

User Statement

Project Outcome

Architecture Decision

Research Finding

Workflow Observation

Performance Benchmark

Memory Merge

Agent Recommendation

---

Source must be traceable.

---

# 12. TIMESTAMPS

Every memory must contain:

Created Timestamp

Last Updated Timestamp

Last Accessed Timestamp

---

Used for audits and retention.

---

# 13. TAGS

Purpose:

Searchability

Examples:

FastAPI

AI

Learning

Architecture

Maintainability

Security

Agent-System

---

Tags improve retrieval.

---

# 14. RELATIONSHIPS

Memories should connect to other memories.

Examples:

Technology Preference
↓
Architecture Decision
↓
Implementation Lesson

---

Relationships create knowledge networks.

---

# 15. IMPORTANCE SCORE

Range:

1 – 10

Factors:

Longevity

Impact

Frequency

Decision Value

Reusability

---

High scores receive higher retrieval priority.

---

# 16. RETENTION LEVELS

Level 1

Temporary

---

Level 2

Standard

---

Level 3

Long-Term

---

Level 4

Permanent

---

Retention level influences archival decisions.

---

# 17. STATUS

Possible Values:

Active

Archived

Deprecated

Merged

Superseded

---

Status prevents outdated memories from polluting decisions.

---

# 18. USER PREFERENCE MEMORIES

Examples:

Preferred Frameworks

Preferred Learning Style

Preferred Communication Style

Preferred Architecture Style

Preferred Workflows

---

These memories receive high retrieval priority.

---

# 19. ENGINEERING PREFERENCE MEMORIES

Examples:

Maintainability > Speed

Evidence > Assumptions

Learning > Blind Automation

Local First

---

Engineering preferences strongly influence decision making.

---

# 20. MCP AND SKILL MEMORIES

Examples:

Firecrawl effective for documentation extraction

Agent Memory MCP preferred for persistence

autoplan useful for large project planning

investigate useful for root-cause analysis

---

These memories improve future workflow selection.

---

# 21. MEMORY MERGING RULES

If similar memories exist:

Compare

Evaluate

Merge

Update Context

Preserve Evidence

Update Confidence

---

Avoid duplication.

---

# 22. MEMORY CONFLICT RULES

Conflicting memories should not overwrite each other automatically.

Prefer:

Context-Based Resolution

Example:

FastAPI preferred for AI Systems

Django preferred for Admin-Heavy Systems

---

Store both with context.

---

# 23. MEMORY RETRIEVAL PRIORITY

Priority Factors:

Relevance

Importance

Confidence

Recency

Relationship Strength

Context Match

---

Most useful memory should appear first.

---

# 24. MEMORY QUALITY RULES

Every stored memory should be:

Accurate

Relevant

Traceable

Actionable

Context-Aware

Evidence-Based

---

Low-quality memories should be reviewed.

---

# 25. FUTURE EVOLUTION

Phase 1

Structured Records

---

Phase 2

Vector Retrieval

---

Phase 3

Relationship Graph

---

Phase 4

Knowledge Graph

---

Phase 5

Self-Organizing Memory Network

---

# 26. FINAL DIRECTIVE

Global Memory exists to preserve long-term intelligence.

Store knowledge.

Store context.

Store evidence.

Store relationships.

Never store isolated facts when contextual knowledge can be preserved.
