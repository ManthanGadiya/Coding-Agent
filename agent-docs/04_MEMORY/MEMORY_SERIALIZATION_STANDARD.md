# MEMORY_SERIALIZATION_STANDARD.md

Version: 1.0

Status: Active

Authority Level: High

Storage Format: TOON

Related Documents:

- GLOBAL_MEMORY_SCHEMA.md
- PROJECT_MEMORY_SCHEMA.md
- MEMORY_RETRIEVAL.md
- MEMORY_ARCHITECTURE.md

---

# 1. PURPOSE

This document defines the serialization standard used by CAMera.

The purpose is to ensure:

Consistency

Compression

Readability

Compatibility

Knowledge Preservation

All internal memory structures must follow this specification.

---

# 2. PHILOSOPHY

CAMera uses:

TOON

(Token Oriented Object Notation)

for internal knowledge representation.

Reasons:

Lower token usage

Higher context density

Better compression

Readable by humans

Readable by agents

---

# 3. SERIALIZATION RULE

Internal Knowledge:

TOON

---

External APIs:

JSON

---

MCP Communication:

JSON

---

Database Representation:

Implementation Choice

---

# 4. MEMORY OBJECT STRUCTURE

Every memory object should follow:

memory:

 id:

 type:

 title:

 content:

 context:

 evidence:

 confidence:

 source:

 relationships:

 metadata:

---

# 5. REQUIRED FIELDS

Every memory must contain:

id

type

title

context

confidence

source

---

Optional fields:

evidence

relationships

metadata

---

# 6. MEMORY ID FORMAT

Pattern:

PREFIX-NUMBER

Examples:

MEM-001

DEC-014

BUG-031

LES-022

RISK-008

---

IDs must remain immutable.

---

# 7. CONFIDENCE FORMAT

Range:

0.00 - 1.00

Examples:

1.00
0.95
0.82
0.61

---

Confidence should be numeric.

Not textual.

---

# 8. RELATIONSHIP FORMAT

relationships:

 related_decisions:

 related_bugs:

 related_lessons:

 related_requirements:

---

Relationships should use IDs.

Never duplicate content.

---

# 9. DECISION FORMAT

decision:

 id:

 title:

 reasoning:

 alternatives:

 tradeoffs:

 owner:

 approved_by:

 confidence:

---

# 10. BUG FORMAT

bug:

 id:

 symptoms:

 root_cause:

 fix:

 validation:

 lesson_learned:

 status:

---

# 11. LESSON FORMAT

lesson:

 id:

 title:

 observation:

 impact:

 confidence:

 reusable:

---

# 12. RISK FORMAT

risk:

 id:

 description:

 likelihood:

 impact:

 mitigation:

 owner:

 status:

---

# 13. MILESTONE FORMAT

milestone:

 id:

 objective:

 completed_work:

 decisions:

 lessons:

 risks:

 blockers:

 completion_date:

---

# 14. KNOWLEDGE ARTIFACT FORMAT

knowledge_artifact:

 id:

 title:

 discovered_from:

 evidence:

 conclusion:

 confidence:

 impact:

 reusable:

---

Knowledge Artifacts represent discovered knowledge.

Not raw memories.

---

# 15. CONTRADICTION RECORD FORMAT

contradiction:

 id:

 memory_a:

 memory_b:

 analysis:

 resolution:

 confidence:

---

Contradictions should be preserved.

Not hidden.

---

# 16. KNOWLEDGE PACKAGE FORMAT

knowledge_package:

 task:

 memories:

 summary:

 graph:

 contradictions:

 confidence:

 recommendations:

---

Knowledge Packages are temporary.

---

# 17. GRAPH REPRESENTATION

graph:

 node:

 relationship:

 node:

---

Example:

JWT Decision

↓

Auth Bug

↓

Auth Lesson

---

# 18. VERSION HISTORY FORMAT

history:

 v1:

 v2:

 v3:

 current:

---

Do not delete history.

Compress history when required.

---

# 19. COMPRESSION FORMAT

compressed_pattern:

 source_count:

 pattern:

 confidence:

 evidence:

---

Compression should preserve knowledge.

Not raw details.

---

# 20. ARCHIVAL FORMAT

archive:

 id:

 original_type:

 archived_date:

 retention_reason:

 retrieval_allowed:

---

Archived knowledge remains searchable.

---

# 21. VALIDATION RULES

All TOON structures must be:

Parseable

Consistent

Traceable

Versioned

Relationship-Aware

---

Invalid structures should be rejected.

---

# 22. JSON CONVERSION RULES

TOON must support:

TOON → JSON

JSON → TOON

without information loss.

---

# 23. FORWARD COMPATIBILITY

New fields may be added.

Existing fields should not be removed.

---

Backward compatibility preferred.

---

# 24. MCP INTEGRATION RULES

Before MCP storage:

Validate TOON

↓

Convert if required

↓

Store

---

After retrieval:

Retrieve

↓

Deserialize

↓

Knowledge Processing

---

# 25. SUCCESS CRITERIA

Serialization succeeds when:

Knowledge preserved

Relationships preserved

Compression effective

Retrieval efficient

Conversion reliable

---

# 26. FAILURE CONDITIONS

Serialization fails when:

Knowledge lost

Relationships broken

History removed

Context discarded

Confidence corrupted

---

# 27. FINAL DIRECTIVE

TOON is the canonical knowledge language of CAMera.

Store knowledge efficiently.

Preserve context.

Preserve relationships.

Preserve history.

Preserve reasoning.

Optimize for intelligence, not storage.