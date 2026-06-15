# MEMORY_RETRIEVAL.md

Version: 1.0

Status: Active

Authority Level: High

Storage Format: TOON

Related Documents:

- MEMORY_ARCHITECTURE.md
- GLOBAL_MEMORY_SCHEMA.md
- PROJECT_MEMORY_SCHEMA.md
- MEMORY_AGENT.md
- DECISION_ENGINE.md

---

# 1. PURPOSE

This document defines how CAMera retrieves knowledge.

Retrieval is not memory lookup.

Retrieval is knowledge reconstruction.

The objective is to rebuild the most useful knowledge network for the current task.

---

# 2. RETRIEVAL PHILOSOPHY

The goal is not:

Find memories.

The goal is:

Find useful knowledge.

A memory system is only valuable if the correct knowledge appears at the correct time.

---

# 3. RETRIEVAL PIPELINE

Task Request

↓

Context Analysis

↓

Retrieval Profile Selection

↓

Memory Search

↓

Relationship Expansion

↓

Contradiction Detection

↓

Knowledge Graph Generation

↓

Pattern Analysis

↓

Knowledge Package Creation

↓

Agent Consumption

---

# 4. RETRIEVAL PRIORITIES

Default Priority Order:

1. Context Match
2. Importance
3. Confidence
4. Outcome Quality
5. Project Frequency
6. Relationship Strength
7. Recency

---

Context always outranks recency.

---

# 5. WEIGHTED RETRIEVAL SCORING

Retrieval Score should evaluate:

Context Match

Importance

Confidence

Outcome Quality

Frequency

Relationship Strength

Recency

---

Example:

Final Score =
(Context × Weight)
+
(Importance × Weight)
+
(Confidence × Weight)
+
(Outcome Quality × Weight)
+
(Frequency × Weight)
+
(Relationship Strength × Weight)
+
(Recency × Weight)

---

No single factor should dominate retrieval quality.

---

# 6. AGENT-AWARE RETRIEVAL

Different agents require different knowledge.

The best memory is not the most important memory.

The best memory is the most useful memory for the current task.

---

# 7. MANAGER RETRIEVAL PROFILE

Priority:

Project Status

Risks

Milestones

Dependencies

Decisions

Lessons Learned

Improvement Opportunities

---

# 8. ARCHITECT RETRIEVAL PROFILE

Priority:

Architecture Decisions

Tradeoffs

Constraints

Technology Comparisons

Scalability Findings

Architecture Lessons

---

# 9. PLANNER RETRIEVAL PROFILE

Priority:

Requirements

Research

Dependencies

Risks

Lessons

Decision History

Roadmaps

---

# 10. CODER RETRIEVAL PROFILE

Priority:

Implementation Patterns

Coding Standards

Past Solutions

Project Structure

Technical Debt

Refactoring History

---

# 11. TESTER RETRIEVAL PROFILE

Priority:

Test Results

Coverage Reports

Regression History

Validation Rules

Quality Findings

Testing Lessons

---

# 12. DEBUGGER RETRIEVAL PROFILE

Priority:

Bug Records

Root Cause Records

Lessons Learned

Architecture Decisions

Technical Debt

Related Implementations

---

# 13. REVIEWER RETRIEVAL PROFILE

Priority:

Architecture Reviews

Security Findings

Maintainability Findings

Complexity Analysis

Technical Debt

Quality Lessons

---

# 14. MEMORY AGENT RETRIEVAL PROFILE

Priority:

Knowledge Relationships

Memory Quality

Duplicate Records

Retention Candidates

Compression Candidates

Knowledge Artifacts

---

# 15. MODE-AWARE RETRIEVAL

Retrieval should adapt to task type.

Modes:

Planning

Architecture

Implementation

Testing

Debugging

Review

Learning

Research

Optimization

---

# 16. PLANNING MODE

Retrieve:

Requirements

Research

Risks

Dependencies

Milestones

Lessons

---

# 17. ARCHITECTURE MODE

Retrieve:

Architecture Decisions

Tradeoffs

Technology Evaluations

Constraints

Scalability Findings

---

# 18. IMPLEMENTATION MODE

Retrieve:

Implementation Patterns

Past Solutions

Coding Standards

Project Structure

---

# 19. DEBUGGING MODE

Retrieve:

Bug Records

Root Causes

Lessons Learned

Architecture Decisions

Technical Debt

Related Implementations

---

Debugging retrieval should prioritize understanding failures.

---

# 20. REVIEW MODE

Retrieve:

Architecture Reviews

Security Findings

Quality Reports

Complexity Findings

Technical Debt

---

# 21. RELATIONSHIP EXPANSION

Retrieval should not stop at direct matches.

Expand:

Decision

↓

Architecture

↓

Implementation

↓

Bug

↓

Lesson

↓

Improvement

---

Related knowledge increases reasoning quality.

---

# 22. KNOWLEDGE GRAPH GENERATION

Retrieved memories should generate a temporary knowledge graph.

Example:

Authentication

├── JWT Decision

├── Auth Architecture

├── Auth Bug

├── Auth Lesson

└── Auth Security Finding

---

Knowledge graphs exist by default for current tasks.

---

# 23. TEMPORARY KNOWLEDGE GRAPHS

Knowledge graphs should be temporary.

Default Behavior:

Generate

Use

Discard

---

Only valuable discoveries should persist.

---

# 24. KNOWLEDGE ARTIFACT CREATION

If retrieval reveals valuable patterns:

Memory Agent may create:

Knowledge Artifacts

---

Example:

Observed Across 27 Projects:

JWT + Refresh Tokens reduced authentication failures.

↓

Create Knowledge Artifact

---

Knowledge Artifacts represent discovered wisdom.

---

# 25. CONTRADICTION DETECTION

Retrieval should identify contradictions.

Example:

Use JWT

Avoid JWT

---

Contradictions should not be hidden.

---

# 26. CONTRADICTION ANALYSIS

When contradictions exist:

Analyze Context

Analyze Evidence

Analyze Outcomes

Generate Resolution

---

Example:

JWT Recommended:

- APIs
- Agent Systems

JWT Discouraged:

- Immediate Revocation Systems

Conclusion:

Context Dependent

---

# 27. TOP-N RETRIEVAL

Do not return every memory.

Return:

Top N Relevant Memories

---

Default:

Simple Tasks:
Top 5

Moderate Tasks:
Top 10

Complex Tasks:
Top 15

Large Projects:
Top 20

---

# 28. PATTERN SUMMARIZATION

Remaining memories should be summarized.

Example:

Analyzed:

47 Authentication Memories

Observed Pattern:

JWT + Refresh Tokens most successful.

Confidence:

0.93

---

# 29. KNOWLEDGE PACKAGE GENERATION

Agents should consume Knowledge Packages.

Not raw memories.

---

Knowledge Package Contents:

Top Memories

Pattern Summary

Knowledge Graph

Contradictions

Confidence

Recommended Knowledge

Related Decisions

Related Lessons

---

# 30. RETRIEVAL OUTPUT FORMAT

Example:

knowledge_package:

 task:
  Authentication Design

 memories:
  ...

 summary:
  ...

 contradictions:
  ...

 graph:
  ...

 confidence:
  0.93

 recommendations:
  ...

---

# 31. MEMORY MCP INTEGRATION

Primary Retrieval Source:

Agent Memory MCP

Responsibilities:

Memory Search

Relationship Expansion

Artifact Retrieval

Pattern Discovery

Knowledge Packaging

---

# 32. RETRIEVAL QUALITY METRICS

Evaluate:

Relevance

Precision

Knowledge Coverage

Context Accuracy

Contradiction Handling

Reasoning Support

---

# 33. FAILURE CONDITIONS

Retrieval fails when:

Important knowledge missed

Irrelevant knowledge dominates

Contradictions hidden

Context ignored

Knowledge graphs inaccurate

---

# 34. SUCCESS METRICS

Retrieval succeeds when:

Decision quality improves

Research time decreases

Repeated mistakes decrease

Reasoning quality improves

Knowledge reuse increases

---

# 35. FINAL DIRECTIVE

Retrieval is not memory lookup.

Retrieval is knowledge reconstruction.

Prioritize context.

Expand relationships.

Detect contradictions.

Generate knowledge graphs.

Create knowledge packages.

Deliver the most useful knowledge for the current task.

Transform memory into intelligence.