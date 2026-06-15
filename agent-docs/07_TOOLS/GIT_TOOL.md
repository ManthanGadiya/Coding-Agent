# GIT_TOOL.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

- TOOL_REGISTRY.md
- PERMISSION_SYSTEM.md
- HUMAN_APPROVAL_RULES.md
- SAFETY_RULES.md
- RELEASE_WORKFLOW.md

---

# 1. PURPOSE

This document defines the Git Tool used by CAMera.

The Git Tool provides repository management capabilities while respecting governance, permissions, approvals, and safety requirements.

---

# 2. CORE PHILOSOPHY

The Git Tool executes Git operations.

The Git Tool does not determine repository strategy.

Decision making belongs to agents.

Governance belongs to the Manager.

---

# 3. RESPONSIBILITIES

The Git Tool may:

- Create Branches
- Checkout Branches
- Delete Branches
- Create Commits
- Push Changes
- Pull Changes
- Create Tags
- Inspect Repository State

---

# 4. NON-RESPONSIBILITIES

The Git Tool is not responsible for:

- Planning
- Architecture Decisions
- Approval Decisions
- Merge Decisions
- Release Decisions
- Governance Decisions

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

Git Tool

↓

Execution

↓

Result Analysis

---

# 6. REQUIRED CAPABILITIES

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

Operations require matching capabilities.

---

# 7. BRANCH STRATEGY

Branching should be determined by:

- Change Scope
- Risk Level
- Repository Classification
- Project Policy

---

# 8. SMALL CHANGES

Examples:

- Typo Fixes
- Documentation Updates
- Small Bug Fixes

---

Direct commit may be allowed.

Repository policy determines behavior.

---

# 9. MEDIUM CHANGES

Examples:

- Feature Enhancements
- API Updates
- Test Improvements

---

Feature branch recommended.

Examples:

feature/auth-improvement

feature/api-enhancement

---

# 10. LARGE CHANGES

Examples:

- Major Refactoring
- Architecture Updates
- Database Migration
- Authentication Rewrite

---

Dedicated branch required.

Examples:

refactor/auth-system

architecture/memory-v2

---

# 11. CRITICAL CHANGES

Examples:

- Constitution Changes
- Safety Rule Changes
- Permission Model Changes
- Production Infrastructure Changes

---

Protected workflow required.

Manager awareness required.

Additional review may be required.

---

# 12. BRANCH CREATION AUTHORITY

Branch strategy is determined by:

Manager

Workflow Rules

Repository Policy

---

The Git Tool executes branch operations.

It does not decide branch strategy.

---

# 13. COMMIT STRATEGY

Commit frequency depends on task size.

---

# 14. SMALL TASKS

Workflow:

Implementation

↓

Testing

↓

Review

↓

Single Final Commit

---

# 15. MAJOR TASKS

Workflow:

Implementation

↓

Checkpoint Commit

↓

Implementation

↓

Checkpoint Commit

↓

Testing

↓

Review

↓

Final Commit

---

# 16. CHECKPOINT COMMITS

Checkpoint commits exist to:

- Reduce rollback risk
- Preserve progress
- Improve recovery
- Protect long-running work

---

Checkpoint commits should occur at logical milestones.

Not after every modification.

---

# 17. CHECKPOINT TRIGGERS

Examples:

- 50+ Files Modified
- Architecture Layer Completed
- Database Migration Completed
- Feature Phase Completed
- Risky Refactor Completed

---

Manager may recommend checkpoints.

---

# 18. COMMIT MESSAGE POLICY

Commit messages should be:

Clear

Descriptive

Action Oriented

---

Examples:

feat(authentication): add login workflow

fix(database): resolve migration issue

refactor(api): simplify service layer

---

# 19. POST-COMMIT POLICY

Commit creation does not imply publication.

Commit and publish are separate stages.

---

# 20. COMMIT VS PUBLICATION

Commit

↓

Local Repository

---

Push

↓

Remote Repository

---

Merge

↓

Shared Branch

---

Release

↓

Users

---

Each stage increases visibility and risk.

---

# 21. PUSH AUTHORITY

The Git Tool may perform pushes when:

Capability Exists

Approval Exists

Safety Checks Pass

Manager Authorizes Progression

---

The Git Tool does not decide when a push should occur.

---

# 22. MERGE POLICY

The Git Tool executes merge operations.

The Git Tool does not approve merges.

Merge authority belongs to governance workflows.

---

# 23. PUSH PROTECTION

Before push:

Evaluate:

- Secret Exposure
- Credential Leakage
- Safety Violations
- Approval Requirements

---

Unsafe pushes must be blocked.

---

# 24. TAG MANAGEMENT

Tags may be used for:

- Releases
- Milestones
- Recovery Points

---

Tag strategy is determined by project workflows.

---

# 25. REPOSITORY INSPECTION

The Git Tool may inspect:

- Status
- Branches
- History
- Tags
- Diffs

---

Inspection is read-only.

---

# 26. FAILURE HANDLING

If a Git operation fails:

Record Failure

↓

Return Details

↓

Agent Decision

---

Recovery belongs to agents.

---

# 27. AUDIT REQUIREMENTS

Git operations should record:

Agent

Operation

Repository

Timestamp

Risk Level

Outcome

---

All operations should be auditable.

---

# 28. ESCALATION CONDITIONS

Escalate when:

- Capability Missing
- Approval Missing
- Safety Violation
- Protected Branch Access
- Secret Detection
- Unknown Repository State

---

Manager owns escalation routing.

---

# 29. SUCCESS CONDITIONS

Git Tool succeeds when:

Operations Complete Successfully

Repository Integrity Preserved

Safety Maintained

Governance Preserved

Auditability Maintained

---

# 30. FAILURE CONDITIONS

Git Tool fails when:

Unauthorized Operations Execute

Protected Workflows Bypassed

Safety Violations Ignored

Audit Trails Missing

Governance Violated

---

# 31. FINAL DIRECTIVE

Manage repositories safely.

Protect history integrity.

Separate commits from publication.

Respect governance.

Respect safety.

The Git Tool executes.

It does not govern.