# MEMORY_RETENTION_POLICY.md

Version: 1.0

Status: Active

Authority Level: High

Storage Format: TOON

Related Documents:

- GLOBAL_MEMORY_SCHEMA.md
- PROJECT_MEMORY_SCHEMA.md
- MEMORY_RETRIEVAL.md
- MEMORY_UPDATES.md
- MEMORY_COMPRESSION.md
- MEMORY_AGENT.md

---

# 1. PURPOSE

This document defines how CAMera retains, archives, compresses, and removes memory.

The objective is not maximum retention.

The objective is maximum knowledge value.

Knowledge should survive.

Noise should not.

---

# 2. CORE PHILOSOPHY

Preserve Knowledge.

Not Data.

Preserve Wisdom.

Not History.

Preserve Relationships.

Not Clutter.

---

# 3. RETENTION GOALS

The retention system should:

Maintain Memory Quality

Reduce Noise

Improve Retrieval

Preserve Knowledge

Support Long-Term Learning

Prevent Memory Pollution

---

# 4. MEMORY LIFECYCLE

Created

↓

Active

↓

Referenced

↓

Compressed

↓

Archived

↓

Historical Summary

↓

Retired

---

Not every memory reaches every stage.

---

# 5. RETENTION LEVELS

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

# 6. TEMPORARY RETENTION

Examples:

Transient Observations

Low Confidence Notes

Unvalidated Findings

Session-Specific Information

---

Review Period:

30 Days

---

# 7. STANDARD RETENTION

Examples:

Project Tasks

Milestones

Routine Decisions

Research Results

---

Review Period:

180 Days

---

# 8. LONG-TERM RETENTION

Examples:

Architecture Decisions

Lessons Learned

Major Discoveries

Workflow Patterns

---

Review Period:

1 Year

---

# 9. PERMANENT RETENTION

Examples:

User Preferences

Engineering Principles

Approved Decision Rules

High-Value Knowledge Artifacts

Core System Knowledge

---

Never automatically removed.

---

# 10. RETENTION FACTORS

Evaluate:

Importance

Confidence

Reusability

Frequency

Relationship Strength

Outcome Quality

Knowledge Density

---

# 11. RETENTION SCORE

Retention decisions should use:

Importance

+

Confidence

+

Relationships

+

Frequency

+

Outcome Quality

---

No single factor should dominate.

---

# 12. ACTIVE MEMORY

Active memory participates fully in retrieval.

Priority:

Highest

---

# 13. ARCHIVED MEMORY

Archived memory remains searchable.

Archived memory receives:

Lower Retrieval Priority

---

Archive does not mean forgotten.

---

# 14. COMPRESSION BEFORE ARCHIVAL

Before archival:

Evaluate Compression.

---

Preferred Process:

Compress

↓

Archive

↓

Delete Raw Memory Only If Safe

---

# 15. DELETION POLICY

Deletion is the final option.

Deletion requires:

Compression Complete

Knowledge Preserved

Manager Approval

Audit Record

---

# 16. RAW MEMORY DELETION

Raw memory may be deleted when:

Knowledge Extracted

Patterns Preserved

Relationships Captured

Confidence Low

Historical Value Low

---

# 17. HISTORICAL SUMMARIES

Before deletion:

Generate Historical Summary.

Example:

historical_summary:

 source_count:
  847

 common_patterns:
  ...

 lessons:
  ...

 confidence:
  ...

---

Historical summaries should remain searchable.

---

# 18. RETENTION REVIEW TRIGGERS

Review when:

Memory Age Threshold Reached

Confidence Changes

Knowledge Artifact Created

Relationship Network Changes

Project Archived

---

# 19. STALE MEMORY DETECTION

Indicators:

Never Retrieved

Low Confidence

No Relationships

No Evidence

No Reuse

---

Stale memories should be reviewed.

---

# 20. MEMORY HEALTH METRICS

Evaluate:

Noise Ratio

Knowledge Density

Duplicate Count

Archive Growth

Compression Effectiveness

Retrieval Quality

---

# 21. PROJECT MEMORY RETENTION

Retain:

Architecture

Decisions

Lessons

Milestones

Bugs

Risks

Knowledge Artifacts

---

Compress:

Routine Activity

Minor Logs

Temporary Findings

---

# 22. GLOBAL MEMORY RETENTION

Retain:

Preferences

Goals

Engineering Principles

Learning Preferences

Approved Rules

Knowledge Artifacts

---

Highest retention priority.

---

# 23. RELATIONSHIP RETENTION

Relationships often have more value than individual memories.

Prefer preserving:

Knowledge Networks

Decision Chains

Architecture Evolution

Bug → Lesson Links

---

# 24. APPROVED RULE RETENTION

Approved Decision Rules:

Permanent

Unless reviewed.

---

Rule removal requires:

Manager Review

Evidence Review

Historical Analysis

---

# 25. KNOWLEDGE ARTIFACT RETENTION

Knowledge Artifacts should remain active while:

Confidence remains acceptable

Evidence remains valid

Reuse remains significant

---

# 26. RETENTION AUDITS

Periodic audits should:

Review Old Memories

Evaluate Retrieval Value

Compress Noise

Update Confidence

Archive Obsolete Knowledge

---

# 27. MEMORY MCP RESPONSIBILITIES

Agent Memory MCP:

Store

Archive

Retrieve

Compress

Audit

Track Retention State

---

# 28. FAILURE CONDITIONS

Retention fails when:

Knowledge Lost

Important Context Removed

Relationships Broken

Useful Patterns Deleted

Noise Dominates Retrieval

---

# 29. SUCCESS METRICS

Retention succeeds when:

Knowledge Density Improves

Retrieval Quality Improves

Storage Waste Decreases

Decision Quality Improves

Learning Accelerates

---

# 30. FINAL DIRECTIVE

Retain knowledge.

Compress experience.

Preserve wisdom.

Archive history.

Delete only when knowledge has been safely preserved.

CAMera should become wiser over time,

not merely larger.