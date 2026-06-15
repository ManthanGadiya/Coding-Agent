# DOCKER_TOOL.md

Version: 1.0

Status: Active

Authority Level: Medium

Related Documents:

- TOOL_REGISTRY.md
- TERMINAL_TOOL.md
- PERMISSION_SYSTEM.md
- SAFETY_RULES.md

---

# 1. PURPOSE

This document defines the Docker Tool used by CAMera.

The Docker Tool provides container management capabilities.

Docker is treated as an execution environment rather than a governance system.

---

# 2. CORE PHILOSOPHY

The Docker Tool executes container operations.

The Docker Tool does not make deployment decisions.

The Docker Tool does not make architecture decisions.

Agents decide.

The tool executes.

---

# 3. RESPONSIBILITIES

The Docker Tool may:

- Build Containers
- Run Containers
- Stop Containers
- Restart Containers
- Inspect Containers
- View Logs
- Execute Commands In Containers
- Manage Docker Compose Projects

---

# 4. NON-RESPONSIBILITIES

The Docker Tool is not responsible for:

- Deployment Strategy
- Environment Design
- Architecture Decisions
- Governance Decisions
- Approval Decisions

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

Docker Tool

↓

Execution

↓

Result Analysis

---

# 6. REQUIRED CAPABILITIES

Examples:

docker_build

docker_run

docker_stop

docker_restart

docker_logs

docker_exec

docker_compose

---

Operations require matching capabilities.

---

# 7. COMMON OPERATIONS

Examples:

docker build

docker run

docker stop

docker restart

docker logs

docker exec

docker compose up

docker compose down

---

# 8. RISK CLASSIFICATION

Low Risk

- View Logs
- Inspect Containers

Medium Risk

- Build Containers
- Start Containers
- Stop Containers

High Risk

- Delete Containers
- Delete Volumes
- Remove Images

Critical Risk

- Production Container Removal
- Destructive Environment Cleanup

---

# 9. CONTAINER LOGS

Container logs may be:

Collected

Summarized

Referenced

---

Large logs should not be inserted directly into context.

---

# 10. FAILURE HANDLING

If a Docker operation fails:

Record Failure

↓

Return Error Information

↓

Agent Determines Recovery

---

Recovery belongs to agents.

---

# 11. AUDIT REQUIREMENTS

Docker operations should record:

Agent

Operation

Container

Timestamp

Outcome

Risk Level

---

All operations should remain auditable.

---

# 12. SECURITY REQUIREMENTS

Docker operations must respect:

Permission System

Approval Rules

Safety Rules

Governance Rules

---

Unauthorized operations are prohibited.

---

# 13. ESCALATION CONDITIONS

Escalate when:

Capability Missing

Approval Missing

Safety Violation

Critical Environment Impact

Unknown Risk

---

Manager owns escalation routing.

---

# 14. SUCCESS CONDITIONS

Docker Tool succeeds when:

Operations Complete Successfully

Container State Managed Correctly

Safety Maintained

Governance Maintained

Auditability Preserved

---

# 15. FAILURE CONDITIONS

Docker Tool fails when:

Unauthorized Operations Execute

Safety Rules Bypassed

Audit Trails Missing

Governance Violated

---

# 16. FINAL DIRECTIVE

Manage containers safely.

Respect governance.

Respect safety.

Provide execution visibility.

The Docker Tool executes.

It does not govern.