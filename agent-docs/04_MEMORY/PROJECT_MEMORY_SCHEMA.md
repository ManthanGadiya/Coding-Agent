# PROJECT_MEMORY_SCHEMA.md

Version: 1.0

Status: Active

Authority Level: High

Storage Format: TOON

Related Documents:

* MEMORY_ARCHITECTURE.md
* GLOBAL_MEMORY_SCHEMA.md
* MEMORY_AGENT.md
* AGENT_CONSTITUTION.md

---

# 1. PURPOSE

Project Memory stores knowledge specific to a single project.

Unlike Global Memory:

Project Memory preserves:

* Decisions
* Architecture Evolution
* Requirements
* Bugs
* Lessons Learned
* Milestones
* Risks
* Tradeoffs
* Technical Discoveries

The goal is to preserve project intelligence.

Not project history.

---

# 2. CORE PHILOSOPHY

Project Memory should answer:

Why was this built?

Why was this decision made?

What failed?

What succeeded?

What was learned?

What should future work know?

---

# 3. STORAGE FORMAT

All Project Memory records shall use TOON.

External integrations may use JSON.

Internal knowledge representation remains TOON.

---

# 4. PROJECT MEMORY CATEGORIES

Categories:

Decision

Architecture

Requirement

Milestone

Bug

Lesson

Risk

Constraint

Dependency

Research

Optimization

Technical Debt

Workflow

Discovery

---

# 5. DECISION RECORD

Example:

decision:

id:
DEC-001

title:
Use SQLite

reasoning:
Local-first deployment
Single-user environment

alternatives:
PostgreSQL
MySQL

tradeoffs:

pros:
Simple setup
No server management

cons:
Limited concurrency
Future scaling constraints

owner:
Architect

approved_by:
Manager

confidence:
0.95

---

# 6. DECISION HISTORY

Every major decision should preserve history.

Do not delete previous versions.

Compress them.

Example:

decision:

id:
DEC-014

current:
PostgreSQL
Redis
CQRS

history:

v1:
MongoDB

v4:
PostgreSQL

v9:
PostgreSQL
Redis

lessons:

MongoDB removed due to transaction needs

Redis introduced for latency reduction

CQRS introduced for scale requirements

---

# 7. REQUIREMENT RECORD

requirement:

id:
REQ-001

title:
Resume Parsing

status:
Completed

priority:
High

source:
User

acceptance_criteria:

Extract Name

Extract Email

Extract Skills

completion_date:
YYYY-MM-DD

---

# 8. ARCHITECTURE RECORD

architecture:

id:
ARC-001

title:
Modular Monolith

reasoning:
Simpler deployment

alternatives:
Microservices

tradeoffs:

pros:
Simpler maintenance

cons:
Less independent scaling

owner:
Architect

---

# 9. MILESTONE RECORD

milestone:

id:
MILE-001

objective:
Build Authentication System

completed_work:

Login

Signup

Session Handling

decisions:

JWT Selected

SQLite Selected

lessons:

Password reset flow required earlier

risks:

Future scaling concerns

blockers:

None

completion_date:
YYYY-MM-DD

---

# 10. BUG RECORD

Bugs should preserve lifecycle.

Example:

bug:

id:
BUG-019

detected:
YYYY-MM-DD

symptoms:
API returns 500

root_cause:
Null user object

fix:
Validation layer added

validation:

Unit Tests Passed

Integration Tests Passed

lesson_learned:
Validate external input

status:
Fixed

---

# 11. LESSON RECORD

lesson:

id:
LES-001

title:
Curriculum Training Improves Stability

context:
Fine-Tuning

observation:
Curriculum stages reduced malformed outputs

impact:
High

confidence:
0.93

reusable:
Yes

---

# 12. RISK RECORD

risk:

id:
RISK-001

description:
Dependency abandonment

likelihood:
Medium

impact:
High

mitigation:
Evaluate alternatives

owner:
Architect

status:
Active

---

# 13. CONSTRAINT RECORD

constraint:

id:
CONST-001

description:
Local execution required

reason:
Privacy

impact:
No cloud-only services

---

# 14. RESEARCH RECORD

research:

id:
RES-001

question:
Best vector database

findings:

Qdrant

Chroma

recommendation:
Qdrant

confidence:
0.89

---

# 15. TECHNICAL DEBT RECORD

technical_debt:

id:
TD-001

description:
Temporary parsing workaround

reason:
Deadline pressure

risk:
Medium

recommended_resolution:
Replace parser

status:
Open

---

# 16. MEMORY RELATIONSHIPS

Records should connect.

Example:

Requirement
↓
Decision
↓
Architecture
↓
Implementation
↓
Bug
↓
Lesson

---

# 17. MEMORY RETRIEVAL PRIORITY

Priority Factors:

Current Project Relevance

Importance

Confidence

Decision Impact

Relationship Strength

Recency

---

# 18. MEMORY QUALITY RULES

All records should be:

Context-Aware

Evidence-Based

Traceable

Actionable

Maintainable

---

# 19. MEMORY COMPRESSION RULE

Older project records should compress into:

Patterns

Lessons

Decision Evolution

Risk Evolution

Architecture Evolution

---

Preserve knowledge.

Reduce noise.

---

# 20. MEMORY AUDIT RULE

Periodic audits should:

Merge duplicates

Update stale records

Compress history

Validate confidence

Archive obsolete knowledge

---

# 21. PROJECT ARCHIVAL

When project completes:

Preserve:

Major Decisions

Lessons

Architecture

Bugs

Milestones

Risks

---

Archive:

Low-value details

Temporary findings

Redundant records

---

# 22. PROJECT MEMORY SUCCESS METRICS

Project Memory succeeds when:

Future developers understand decisions

Repeated mistakes decrease

Debugging becomes easier

Planning becomes faster

Architecture evolution remains visible

---

# 23. FINAL DIRECTIVE

Project Memory exists to preserve project intelligence.

Store decisions.

Store reasoning.

Store tradeoffs.

Store lessons.

Store evolution.

Never store outcomes without context.

Future engineers should understand not only what happened,

but why it happened.
