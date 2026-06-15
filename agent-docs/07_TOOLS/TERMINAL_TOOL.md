# TERMINAL_TOOL.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

- TOOL_REGISTRY.md
- PERMISSION_SYSTEM.md
- HUMAN_APPROVAL_RULES.md
- SAFETY_RULES.md
- AUTONOMY_MODES.md

---

# 1. PURPOSE

This document defines the Terminal Tool used by CAMera.

The Terminal Tool provides controlled command execution capabilities while respecting governance, permissions, approvals, and safety requirements.

---

# 2. CORE PHILOSOPHY

The Terminal Tool executes.

The Terminal Tool does not decide.

Decision making belongs to agents.

Governance belongs to the Manager.

Safety belongs to the Safety System.

---

# 3. RESPONSIBILITIES

The Terminal Tool may:

- Execute Commands
- Run Scripts
- Build Projects
- Run Tests
- Launch Applications
- Monitor Processes
- Capture Output
- Report Results

---

# 4. NON-RESPONSIBILITIES

The Terminal Tool is not responsible for:

- Planning
- Architecture Decisions
- Recovery Strategy
- Governance Decisions
- Approval Decisions
- Safety Decisions

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

Terminal Tool

↓

Execution

↓

Result Analysis

↓

Agent

---

# 6. REQUIRED CAPABILITIES

Examples:

execute_command

run_tests

build_project

run_project

install_package

service_restart

---

Commands require matching capabilities.

---

# 7. COMMAND RISK LEVELS

Every command should be classified as:

Low

Medium

High

Critical

---

# 8. LOW RISK COMMANDS

Examples:

ls

pwd

git status

cat file.txt

---

Workflow:

Safety Analysis

↓

Execute

---

# 9. MEDIUM RISK COMMANDS

Examples:

pytest

npm test

python script.py

docker build

---

Workflow:

Safety Analysis

↓

Execute

↓

Monitor

---

# 10. HIGH RISK COMMANDS

Examples:

git push

npm install

database migration

service restart

---

Workflow:

Safety Analysis

↓

Approval Validation

↓

Execute

---

# 11. CRITICAL RISK COMMANDS

Examples:

rm -rf

database deletion

repository destruction

infrastructure destruction

---

Workflow:

Safety Analysis

↓

Impact Analysis

↓

Impact Report

↓

Approval Validation

↓

Execute

---

# 12. LONG RUNNING COMMANDS

Commands exceeding runtime thresholds require monitoring.

---

Awareness Threshold

Default:

5 Minutes

Action:

Manager Awareness

---

# 13. PROGRESS REPORTING

Long running commands should provide:

- Runtime
- Current Status
- Resource Usage
- Recent Output
- Estimated Remaining Time

---

Commands should remain observable.

---

# 14. ESCALATION THRESHOLDS

Projects may define escalation thresholds.

Examples:

30 Minutes

60 Minutes

120 Minutes

---

Exceeded thresholds may trigger:

Manager Review

User Awareness

---

# 15. OUTPUT MANAGEMENT

Output handling depends on size.

---

Small Outputs

Store and return normally.

---

Medium Outputs

Store output.

Generate summary.

Return summary and relevant details.

---

Large Outputs

Store raw logs.

Generate summary.

Return:

- Status
- Key Results
- Errors
- Warnings
- Log Reference

---

# 16. RAW LOG RETENTION

Raw logs should remain available.

Large outputs should not be inserted directly into agent context.

---

# 17. RESULT EVALUATION

Exit codes should not be interpreted in isolation.

Evaluation should consider:

- Exit Code
- Standard Output
- Standard Error
- Command Context

---

# 18. RESULT CLASSIFICATION

Possible outcomes:

Success

Expected Outcome

Warning

Failure

---

Non-zero exit codes do not automatically indicate failure.

---

# 19. FAILURE HANDLING

On failure the Terminal Tool should provide:

- Exit Code
- Output
- Error Information
- Execution Context

---

# 20. FAILURE RECOVERY POLICY

Recovery decisions belong to agents.

Possible actions:

- Retry
- Alternative Command
- Escalation
- User Awareness

The Terminal Tool does not decide recovery strategies.

---

# 21. AUDIT REQUIREMENTS

Terminal operations should record:

Agent

Command

Timestamp

Duration

Risk Level

Result

Outcome

---

All executions should be auditable.

---

# 22. SECURITY REQUIREMENTS

Terminal execution must respect:

Permission System

Approval Rules

Safety Rules

Governance Rules

---

Unauthorized execution is prohibited.

---

# 23. ESCALATION CONDITIONS

Escalate when:

Capability Missing

Approval Missing

Safety Violation

Unknown Risk

Critical Failure

Long Running Threshold Exceeded

---

# 24. SUCCESS CONDITIONS

Terminal Tool succeeds when:

Commands Execute Correctly

Permissions Respected

Safety Preserved

Auditability Maintained

Governance Preserved

---

# 25. FAILURE CONDITIONS

Terminal Tool fails when:

Unauthorized Commands Execute

Safety Bypassed

Audit Trails Missing

Critical Commands Bypass Controls

Governance Violated

---

# 26. FINAL DIRECTIVE

Execute commands safely.

Monitor execution.

Report outcomes accurately.

Provide complete execution visibility.

The Terminal Tool executes.

Agents determine what to do next.