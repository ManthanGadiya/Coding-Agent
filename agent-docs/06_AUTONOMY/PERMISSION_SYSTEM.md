# PERMISSION_SYSTEM.md

Version: 1.0

Status: Active

Authority Level: Critical

Related Documents:

- AUTONOMY_MODES.md
- HUMAN_APPROVAL_RULES.md
- SAFETY_RULES.md
- AGENT_CONSTITUTION.md
- MANAGER_AGENT.md

---

# 1. PURPOSE

This document defines the permission model used by CAMera.

The objective is to:

Provide Safe Autonomy

Enforce Least Privilege

Prevent Permission Abuse

Enable Auditing

Support Scalability

---

# 2. CORE PHILOSOPHY

Permissions belong to capabilities.

Capabilities belong to roles.

Roles belong to agents.

Agents do not own permissions.

Agents receive permissions through assigned roles.

---

# 3. PERMISSION HIERARCHY

User

↓

Manager

↓

Roles

↓

Capabilities

↓

Actions

---

Only the Manager may authorize capability grants.

---

# 4. PERMISSION MODEL

CAMera uses a capability-based permission system.

Permissions are not assigned directly to agents.

Permissions are assigned to capabilities.

Capabilities are then granted through roles.

---

# 5. CAPABILITY CATEGORIES

Examples:

Filesystem

Git

Terminal

Database

Web

Deployment

Memory

Infrastructure

---

# 6. FILESYSTEM CAPABILITIES

Examples:

read_files

create_files

write_files

rename_files

delete_files

delete_directory

---

# 7. TERMINAL CAPABILITIES

Examples:

execute_command

install_package

run_tests

build_project

run_project

---

# 8. GIT CAPABILITIES

Examples:

git_status

git_commit

git_branch_create

git_branch_delete

git_push

git_pull

git_tag

git_merge

---

# 9. DATABASE CAPABILITIES

Examples:

database_read

database_write

database_migrate

database_delete

---

# 10. MEMORY CAPABILITIES

Examples:

memory_read

memory_write

memory_update

memory_compress

---

# 11. DEPLOYMENT CAPABILITIES

Examples:

deploy_staging

deploy_production

rollback_release

infrastructure_modify

---

# 12. RISK LEVELS

Every capability must have a risk level.

Risk Levels:

Low

Medium

High

Critical

---

# 13. LOW RISK EXAMPLES

read_files

memory_read

git_status

documentation_generation

---

# 14. MEDIUM RISK EXAMPLES

write_files

create_files

run_tests

git_commit

database_write

---

# 15. HIGH RISK EXAMPLES

git_push

install_package

database_migrate

service_restart

---

# 16. CRITICAL RISK EXAMPLES

delete_directory

database_delete

deploy_production

git_merge

force_push

credential_modification

---

# 17. ROLE ASSIGNMENTS

Roles receive capabilities.

Capabilities determine what actions are possible.

---

# 18. PLANNER CAPABILITIES

Default:

read_files

memory_read

web_research

documentation_create

---

Planner does not modify implementation.

---

# 19. ARCHITECT CAPABILITIES

Default:

read_files

memory_read

architecture_documentation

design_analysis

---

Architect does not deploy code.

---

# 20. CODER CAPABILITIES

Default:

read_files

create_files

write_files

execute_command

git_commit

git_branch_create

---

Coder does not merge PRs.

---

# 21. TESTER CAPABILITIES

Default:

read_files

execute_command

run_tests

generate_reports

---

Tester validates systems.

---

# 22. REVIEWER CAPABILITIES

Default:

read_files

analyze_code

generate_review_reports

---

Reviewer does not modify code.

---

# 23. MEMORY AGENT CAPABILITIES

Default:

memory_read

memory_write

memory_update

memory_compress

---

Memory Agent maintains knowledge.

---

# 24. MANAGER CAPABILITIES

Default:

workflow_control

capability_grants

agent_assignment

escalation_control

approval_management

---

Manager governs execution.

---

# 25. PERMANENT CAPABILITIES

Capabilities permanently attached to a role.

Examples:

read_files

memory_read

documentation_generation

---

Permanent capabilities remain active.

---

# 26. SESSION CAPABILITIES

Capabilities granted during a session.

Examples:

temporary_git_push

temporary_database_write

---

Session capabilities expire when the session ends.

---

# 27. TEMPORARY CAPABILITIES

Capabilities granted for a specific task.

Examples:

database_write

delete_files

git_push

---

Temporary capabilities must be revoked after use.

---

# 28. TEMPORARY CAPABILITY WORKFLOW

Agent

↓

Capability Request

↓

Manager Review

↓

Grant

↓

Task Execution

↓

Automatic Revocation

---

Agents cannot self-grant permissions.

---

# 29. CAPABILITY REQUESTS

Requests must include:

Capability

Reason

Task

Expected Duration

Risk Level

---

# 30. CAPABILITY GRANT RECORD

Example:

capability_grant:

 id:
  CAP-001

 capability:
  database_write

 granted_to:
  Coder

 granted_by:
  Manager

 reason:
  Database Migration

 scope:
  Current Task

 expires:
  Task Completion

---

# 31. PERMISSION EXPANSION POLICY

Capabilities may not automatically expand.

Example:

Granted:

delete_files

Required:

delete_directory

---

Workflow:

Agent

↓

New Capability Request

↓

Manager Review

↓

Decision

---

Permission expansion requires review.

---

# 32. LEAST PRIVILEGE PRINCIPLE

Agents should receive:

Only the capabilities required.

No additional permissions.

No speculative permissions.

---

# 33. CAPABILITY REVOCATION

Capabilities should be revoked when:

Task Completes

Session Ends

Risk Increases

Approval Expires

---

Revocation should be automatic whenever possible.

---

# 34. AUDIT REQUIREMENTS

All capability grants must be auditable.

Store:

Who

What

When

Why

Duration

Outcome

---

# 35. VIOLATIONS

Examples:

Unauthorized Access

Self-Granted Permissions

Permission Escalation Attempts

Unauthorized Execution

---

Violations should trigger escalation.

---

# 36. SUCCESS CONDITIONS

Permission system succeeds when:

Least Privilege Maintained

Capabilities Auditable

Permissions Revoked Properly

Governance Preserved

Safety Maintained

---

# 37. FAILURE CONDITIONS

Permission system fails when:

Agents Self-Grant Permissions

Permissions Persist Unnecessarily

Critical Actions Bypass Review

Audit Trails Missing

---

# 38. FINAL DIRECTIVE

Grant only what is needed.

Revoke when no longer needed.

Audit everything.

Trust governance over convenience.

Least privilege is mandatory.