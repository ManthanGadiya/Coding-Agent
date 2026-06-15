# DATABASE_TOOL.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

- TOOL_REGISTRY.md
- PERMISSION_SYSTEM.md
- HUMAN_APPROVAL_RULES.md
- SAFETY_RULES.md
- MEMORY_ARCHITECTURE.md

---

# 1. PURPOSE

This document defines the Database Tool used by CAMera.

The Database Tool provides controlled access to databases while preserving:

- Data Integrity
- Recoverability
- Auditability
- Governance
- Safety

The Database Tool executes database operations.

It does not make governance decisions.

---

# 2. CORE PHILOSOPHY

The Database Tool executes.

Agents decide.

Manager governs.

Safety protects.

---

# 3. RESPONSIBILITIES

The Database Tool may:

- Execute Queries
- Execute Migrations
- Read Data
- Write Data
- Modify Schema
- Create Tables
- Delete Tables
- Inspect Database Metadata

---

# 4. NON-RESPONSIBILITIES

The Database Tool is not responsible for:

- Planning
- Governance
- Architecture Decisions
- Approval Decisions
- Recovery Decisions

---

# 5. TOOL EXECUTION PIPELINE

Agent

↓

Capability Validation

↓

Approval Validation

↓

Safety Validation

↓

Database Tool

↓

Execution

↓

Result Analysis

↓

Agent

---

# 6. REQUIRED CAPABILITIES

Examples:

database_read

database_write

database_migrate

database_delete

database_admin

---

Operations require matching capabilities.

---

# 7. DATABASE OPERATION TYPES

Read Operations

Write Operations

Schema Operations

Migration Operations

Administrative Operations

---

# 8. READ OPERATIONS

Examples:

SELECT

DESCRIBE

SHOW TABLES

Metadata Queries

---

Risk Level:

Low

---

Typical Approval:

Class 0

No Approval Required

---

# 9. WRITE OPERATIONS

Examples:

INSERT

UPDATE

UPSERT

---

Risk Level:

Medium

---

Approval depends on:

Environment

Data Criticality

Project Rules

---

# 10. SCHEMA OPERATIONS

Examples:

CREATE TABLE

ALTER TABLE

CREATE INDEX

DROP INDEX

---

Risk Level:

Medium To High

---

Additional safety validation may apply.

---

# 11. MIGRATION GOVERNANCE

Migration requirements depend on:

Migration Impact

Data Criticality

Environment

Recoverability

---

# 12. LOW IMPACT MIGRATIONS

Examples:

ADD COLUMN

CREATE INDEX

CREATE TABLE

---

Rollback:

Optional

---

# 13. MEDIUM IMPACT MIGRATIONS

Examples:

Rename Column

Constraint Changes

Index Modifications

---

Rollback:

Recommended

---

# 14. HIGH IMPACT MIGRATIONS

Examples:

DROP COLUMN

DROP TABLE

Large Data Transformations

Data Deletion

---

Rollback:

Required

---

Impact Analysis Required

---

# 15. PRODUCTION MIGRATIONS

Production migrations require:

Rollback Plan

Impact Review

Approval Validation

---

Regardless of migration complexity.

---

# 16. MIGRATION PREVIEW

Before migration execution:

Generate Preview

---

Preview should include:

Tables Affected

Columns Affected

Estimated Rows Affected

Risk Classification

Rollback Availability

---

# 17. LARGE DATA OPERATIONS

Large-scale operations should trigger visibility.

---

Evaluation Factors:

Rows Affected

Operation Type

Environment

Data Criticality

---

# 18. LARGE OPERATION POLICY

Large operations require:

Manager Awareness

---

Awareness does not automatically imply approval requirements.

---

# 19. DESTRUCTIVE LARGE OPERATIONS

Examples:

Mass Deletes

Mass Updates

Mass Transformations

---

Additional review may be required depending on risk.

---

# 20. FULL TABLE MODIFICATIONS

Examples:

DELETE FROM users;

UPDATE users SET status='inactive';

---

These operations should trigger:

Manager Awareness

---

Additional escalation may occur depending on:

Environment

Data Criticality

Estimated Impact

---

# 21. RESULT SIZE MANAGEMENT

Database results should be evaluated by size.

---

# 22. SMALL RESULTS

Return directly.

---

# 23. MEDIUM RESULTS

Return directly.

---

# 24. LARGE RESULTS

Apply pagination automatically.

---

Returned Metadata:

Total Rows

Page Number

Page Size

Remaining Pages

---

# 25. OPTIONAL SUMMARIES

Large datasets may include:

Summary Statistics

Schema Overview

Data Distribution Information

---

Pagination remains the default behavior.

---

# 26. METADATA ACCESS

The Database Tool may inspect:

Tables

Indexes

Views

Schemas

Relationships

Database Statistics

---

Metadata access is considered low risk.

---

# 27. FAILURE HANDLING

If a database operation fails:

Record Failure

↓

Return Error Details

↓

Agent Determines Recovery

---

Recovery decisions belong to agents.

---

# 28. AUDIT REQUIREMENTS

Database operations should record:

Agent

Operation

Target

Timestamp

Rows Affected

Risk Level

Outcome

---

All operations should remain auditable.

---

# 29. SECURITY REQUIREMENTS

Database operations must respect:

Permission System

Approval Rules

Safety Rules

Governance Rules

---

Unauthorized operations are prohibited.

---

# 30. ESCALATION CONDITIONS

Escalate when:

Capability Missing

Approval Missing

Safety Violation

Unknown Impact

Critical Dataset Involved

Migration Risk High

---

Manager owns escalation routing.

---

# 31. SUCCESS CONDITIONS

Database Tool succeeds when:

Operations Complete Correctly

Data Integrity Preserved

Safety Maintained

Governance Maintained

Auditability Preserved

---

# 32. FAILURE CONDITIONS

Database Tool fails when:

Unauthorized Access Occurs

Data Corruption Occurs

Safety Rules Bypassed

Audit Trails Missing

Governance Violated

---

# 33. FINAL DIRECTIVE

Protect data.

Preserve recoverability.

Respect governance.

Respect safety.

Maintain visibility.

The Database Tool executes.

It does not govern.