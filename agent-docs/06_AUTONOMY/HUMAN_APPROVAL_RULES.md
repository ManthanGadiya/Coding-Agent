# HUMAN_APPROVAL_RULES.md

Version: 1.0

Status: Active

Authority Level: Critical

Related Documents:

- AUTONOMY_MODES.md
- PERMISSION_SYSTEM.md
- SAFETY_RULES.md
- AGENT_CONSTITUTION.md
- MANAGER_AGENT.md

---

# 1. PURPOSE

This document defines when human approval is required.

The objective is to:

Preserve Human Authority

Prevent Unsafe Actions

Enable Responsible Autonomy

Reduce Approval Fatigue

Maintain Transparency

---

# 2. CORE PHILOSOPHY

Approval requirements should be proportional to risk.

Low-risk actions should remain efficient.

High-risk actions should require stronger oversight.

Critical actions should always involve humans.

---

# 3. APPROVAL CLASSES

Class 0

No Approval Required

---

Class 1

Session Approval

---

Class 2

Project Approval

---

Class 3

Explicit Approval Every Time

---

# 4. CLASS 0

No Approval Required

Examples:

- read_files
- memory_read
- git_status
- documentation_generation

---

# 5. CLASS 1

Session Approval

Examples:

- git_commit
- create_files
- write_files
- run_tests

---

Approval remains valid until the current session ends.

---

# 6. CLASS 2

Project Approval

Examples:

- git_push
- install_package
- database_migrate

---

Approval applies only to the current project.

Approvals do not transfer between projects.

---

# 7. CLASS 3

Explicit Approval Every Time

Examples:

- deploy_production
- database_delete
- delete_repository
- force_push
- credential_rotation

---

Explicit approval is always required.

---

# 8. CAPABILITY-BASED APPROVAL

Approval requirements belong to capabilities.

Agents do not own approvals.

Capabilities determine approval requirements.

---

# 9. RISK-BASED APPROVAL

Approval requirements should consider:

- Capability Risk
- Project Risk
- Impact Scope
- Reversibility

---

# 10. SESSION APPROVALS

Session approvals remain active until:

- Session Ends
- User Revokes Approval
- Risk Changes
- Policy Changes
- Project Changes

---

Session approvals do not expire after individual tasks.

---

# 11. PROJECT APPROVALS

Project approvals apply only to:

- Current Project
- Approved Capability

---

Project approvals do not transfer.

---

# 12. APPROVAL REVALIDATION

Approvals remain valid only while approval assumptions remain valid.

---

Revalidation required when:

- Project Classification Changes
- Risk Level Changes
- Repository Trust Changes
- Governance Changes
- Safety Rule Changes

---

# 13. REVALIDATION WORKFLOW

Change Detected

↓

Manager

↓

Suspend Approval

↓

Notify User

↓

Revalidation

↓

Resume

---

# 14. POLICY CHANGE CONFIRMATION

Changes affecting autonomy require confirmation.

Examples:

- Enable Full Autonomy
- Disable Auto Push
- Modify Approval Policies
- Change Repository Trust Level

---

Workflow:

Request

↓

Impact Summary

↓

Confirmation

↓

Apply Change

↓

Memory Update

---

# 15. CRITICAL ACTIONS

Critical actions always require approval.

Examples:

- Production Deployment
- Repository Deletion
- Database Deletion
- Force Push
- Secret Rotation

---

Critical actions cannot receive permanent approval.

---

# 16. IRREVERSIBLE ACTIONS

Irreversible actions require:

Impact Analysis

↓

Impact Report

↓

Explicit Confirmation

↓

Execution

---

Examples:

- Delete Project
- Delete Repository
- Delete Production Data
- Destroy Infrastructure

---

# 17. IMPACT REPORTS

Impact reports should include:

Target

Affected Resources

Risk Level

Recovery Difficulty

Rollback Availability

Recommendation

---

# 18. USER REVOCATION

Users may revoke approvals at any time.

Workflow:

User Request

↓

Manager

↓

Confirmation

↓

Approval Revoked

↓

Memory Update

---

# 19. APPROVAL AUDIT LOG

All approvals should record:

Who

What

When

Why

Scope

Duration

Outcome

---

# 20. HUMAN AUTHORITY

Humans remain the final authority.

No approval mechanism may override human decisions.

---

# 21. SUCCESS CONDITIONS

Approval system succeeds when:

- Human Authority Preserved
- Approval Fatigue Reduced
- Risks Managed
- Actions Auditable
- Governance Preserved

---

# 22. FAILURE CONDITIONS

Approval system fails when:

- Critical Actions Bypass Approval
- Approvals Transfer Improperly
- Revalidation Ignored
- Audit Trails Missing
- Human Authority Overridden

---

# 23. FINAL DIRECTIVE

Minimize unnecessary interruptions.

Never minimize critical oversight.

Keep humans informed.

Require approval when risk justifies it.

Human authority is final.