# FILESYSTEM_TOOL.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

- TOOL_REGISTRY.md
- PERMISSION_SYSTEM.md
- HUMAN_APPROVAL_RULES.md
- SAFETY_RULES.md
- TASK_EXECUTION_PIPELINE.md

---

# 1. PURPOSE

This document defines the Filesystem Tool used by CAMera.

The Filesystem Tool is responsible for:

- Reading Files
- Creating Files
- Modifying Files
- Renaming Files
- Deleting Files
- Managing Directories

The tool provides controlled access to project files while respecting governance, permissions, and safety requirements.

---

# 2. CORE PHILOSOPHY

The Filesystem Tool executes.

The Filesystem Tool does not decide.

Decision making belongs to agents.

Governance belongs to the Manager.

Safety belongs to the Safety System.

---

# 3. RESPONSIBILITIES

The Filesystem Tool may:

- Read Files
- Create Files
- Modify Files
- Rename Files
- Delete Files
- Create Directories
- Delete Directories
- Search Files
- Inspect File Metadata

---

# 4. NON-RESPONSIBILITIES

The Filesystem Tool is not responsible for:

- Architecture Validation
- Code Review
- Testing
- Governance Decisions
- Approval Decisions
- Safety Decisions

These responsibilities belong to other system components.

---

# 5. FILE OPERATIONS

Supported operations:

read_file

create_file

write_file

append_file

rename_file

delete_file

create_directory

delete_directory

list_directory

search_files

---

# 6. TOOL EXECUTION PIPELINE

Agent

↓

Capability Validation

↓

Approval Validation

↓

Safety Validation

↓

Filesystem Tool

↓

Execution

↓

Result Validation

---

The tool must never bypass governance controls.

---

# 7. REQUIRED CAPABILITIES

Examples:

read_files

create_files

write_files

rename_files

delete_files

delete_directory

---

Operations require matching capabilities.

---

# 8. READ OPERATIONS

Examples:

read_file

list_directory

search_files

---

Risk Level:

Low

---

Typical Approval:

Class 0

No Approval Required

---

# 9. CREATE OPERATIONS

Examples:

create_file

create_directory

---

Risk Level:

Medium

---

Typical Approval:

Class 1

Session Approval

---

# 10. WRITE OPERATIONS

Examples:

write_file

append_file

---

Risk Level:

Medium

---

Typical Approval:

Class 1

Session Approval

---

# 11. DELETE OPERATIONS

Examples:

delete_file

delete_directory

---

Risk Level:

High To Critical

---

Approval requirements depend on:

Scope

Impact

Project Classification

Safety Rules

---

# 12. DIRECT MODIFICATION POLICY

CAMera uses direct file modification.

Workflow:

Read File

↓

Modify File

↓

Write File

---

The Filesystem Tool does not require:

Diff Generation

Patch Generation

Intermediate Validation

---

Validation is handled by:

Tester

Reviewer

Workflow Validation

---

# 13. READ BEFORE WRITE

Before modifying a file:

The current file should be read.

This ensures modifications are based on the latest version.

---

# 14. POST-WRITE VERIFICATION

After modification:

Verify:

File Exists

Operation Succeeded

Content Accessible

---

Verification confirms successful execution.

---

# 15. MASS MODIFICATION POLICY

Filesystem operations should track modification scope.

---

Normal Changes

1–50 Files

Action:

Proceed

---

Large Changes

51–200 Files

Action:

Manager Awareness

---

Massive Changes

200+ Files

Action:

Manager Review

---

Awareness does not automatically imply approval requirements.

---

# 16. CRITICAL FILES

Some files require additional protection.

Examples:

AGENT_CONSTITUTION.md

SAFETY_RULES.md

PERMISSION_SYSTEM.md

HUMAN_APPROVAL_RULES.md

SYSTEM_ARCHITECTURE.md

MEMORY_ARCHITECTURE.md

---

Criticality should be evaluated using:

File Importance

Governance Impact

System Impact

Architecture Impact

---

# 17. MINOR CRITICAL FILE CHANGES

Examples:

Typos

Formatting

Documentation Clarifications

---

Action:

Manager Awareness

---

# 18. MAJOR CRITICAL FILE CHANGES

Examples:

Governance Changes

Safety Changes

Permission Changes

Architecture Changes

Authority Changes

---

Action:

Manager Review

---

Potentially:

User Awareness

---

# 19. DESTRUCTIVE OPERATIONS

Examples:

Delete Project

Delete Repository Contents

Delete Critical Directories

Mass Deletion

---

Require:

Safety Validation

Impact Analysis

Approval Validation

---

# 20. PROTECTED DIRECTORIES

Directories may be classified as:

Protected

Critical

System

---

Additional safeguards may apply.

---

# 21. FILE SEARCH

Filesystem Tool may perform:

Name Search

Pattern Search

Content Search

Metadata Search

---

Search operations are read-only.

---

# 22. FILE METADATA ACCESS

The tool may inspect:

File Size

Creation Date

Modification Date

Permissions

Path Information

---

Metadata access is considered low risk.

---

# 23. FAILURE HANDLING

If an operation fails:

Record Failure

↓

Retry If Safe

↓

Escalate If Necessary

↓

Notify Manager

---

Failures should be logged.

---

# 24. AUDIT REQUIREMENTS

Filesystem operations should record:

Agent

Operation

Target

Timestamp

Result

Risk Level

Outcome

---

All operations should be auditable.

---

# 25. SECURITY REQUIREMENTS

Filesystem operations must not bypass:

Permission System

Approval Rules

Safety Rules

Governance Rules

---

Unauthorized operations are prohibited.

---

# 26. ESCALATION CONDITIONS

Escalate when:

Capability Missing

Approval Missing

Safety Violation Detected

Critical Files Modified

Mass Modification Detected

Unknown Risk Detected

---

Manager owns escalation decisions.

---

# 27. SUCCESS CONDITIONS

Filesystem Tool succeeds when:

Operations Complete Successfully

Permissions Respected

Safety Maintained

Auditability Preserved

Governance Preserved

---

# 28. FAILURE CONDITIONS

Filesystem Tool fails when:

Unauthorized Access Occurs

Safety Rules Bypassed

Audit Trails Missing

Critical Operations Execute Improperly

Governance Violated

---

# 29. FINAL DIRECTIVE

Execute requested filesystem operations.

Respect permissions.

Respect approvals.

Respect safety rules.

Protect critical assets.

Escalate when impact increases.

The Filesystem Tool executes.

It does not govern.