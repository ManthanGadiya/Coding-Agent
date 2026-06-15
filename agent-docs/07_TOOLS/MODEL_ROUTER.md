# MODEL_ROUTER.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

- TOOL_REGISTRY.md
- AUTONOMY_MODES.md
- PERMISSION_SYSTEM.md
- TASK_EXECUTION_PIPELINE.md
- MANAGER_AGENT.md

---

# 1. PURPOSE

This document defines the Model Router used by CAMera.

The Model Router is responsible for selecting the most appropriate model for a task while balancing:

- Correctness
- Safety
- Cost
- Latency
- Privacy
- Resource Utilization

---

# 2. CORE PHILOSOPHY

Select the smallest model capable of safely completing the task.

CAMera should not automatically prefer:

- The cheapest model
- The largest model
- The cloud model
- The local model

Model selection should be context dependent.

---

# 3. ROUTING OBJECTIVES

Priority Order:

1. Correctness
2. Safety
3. Cost Efficiency
4. Speed

---

# 4. ROUTING HIERARCHY

Primary Factor:

Task Complexity

---

Secondary Factor:

Task Risk

---

Third Factor:

Cost Budget

---

Fourth Factor:

Agent Role

---

# 5. TASK COMPLEXITY LEVELS

Low

Examples:

- Documentation Updates
- Variable Renaming
- Simple Queries
- Formatting

---

Medium

Examples:

- Feature Development
- API Design
- Code Reviews
- Test Generation

---

High

Examples:

- Architecture Design
- Multi-Agent Planning
- Large Refactors
- System Design

---

Critical

Examples:

- Production Changes
- Governance Modifications
- Safety System Changes
- Infrastructure Decisions

---

# 6. MODEL SELECTION PHILOSOPHY

Use the smallest capable model.

Never select a larger model simply because it exists.

Model capacity should match task requirements.

---

# 7. LOCAL FIRST STRATEGY

When multiple models are capable:

Prefer:

Local Models

↓

Cloud Models

---

Local execution improves:

Privacy

Cost Efficiency

Availability

Control

---

# 8. CONTEXT FIRST STRATEGY

Local-first is a preference.

Not a rule.

Context determines final selection.

Evaluation Factors:

- Confidence
- Privacy
- Cost
- Latency
- Task Criticality
- Knowledge Freshness
- Risk

---

# 9. MODEL TYPES

Examples:

Small Local Model

Medium Local Model

Large Local Model

Cloud Reasoning Model

Specialized Coding Model

Specialized Research Model

---

Actual models are implementation dependent.

---

# 10. ROUTING WORKFLOW

Task

↓

Complexity Analysis

↓

Risk Analysis

↓

Constraint Analysis

↓

Candidate Models

↓

Selection

↓

Execution

---

# 11. CONFIDENCE EVALUATION

Models may report confidence estimates.

Confidence is one routing signal.

Confidence alone should not determine routing decisions.

---

# 12. CONFIDENCE LEVELS

High

Medium

Low

---

Thresholds are implementation specific.

---

# 13. LOW CONFIDENCE POLICY

Low confidence does not automatically trigger escalation.

Instead:

Response

↓

Confidence Evaluation

↓

Escalation Available

↓

Agent Decision

---

Agents decide whether escalation is required.

---

# 14. PROGRESSIVE ESCALATION

CAMera supports progressive escalation.

Example:

Small Model

↓

Medium Model

↓

Large Model

↓

Cloud Model

---

Escalation should occur only when justified.

---

# 15. ESCALATION FACTORS

Examples:

Low Confidence

High Risk

Repeated Failure

Missing Knowledge

Complex Reasoning Requirements

---

# 16. ESCALATION LOGGING

Escalations should record:

Task

Previous Model

New Model

Reason

Confidence

Timestamp

---

Escalations should remain auditable.

---

# 17. COST MANAGEMENT

Cost should influence routing.

Cost should not override safety or correctness.

---

# 18. PRIVACY MANAGEMENT

Sensitive tasks should prefer local models when feasible.

Examples:

- Proprietary Source Code
- Internal Architecture
- User Data
- Credentials

---

# 19. FRESH KNOWLEDGE REQUIREMENTS

Tasks requiring current information may favor:

Research Models

Cloud Models

Web-Connected Models

---

Freshness requirements should be considered during routing.

---

# 20. SPECIALIZED MODEL ROUTING

Specialized models may be preferred when available.

Examples:

Coding Models

Research Models

Reasoning Models

Vision Models

---

Specialization may outweigh raw size.

---

# 21. FAILURE HANDLING

If a model fails:

Record Failure

↓

Return Failure Information

↓

Agent Decision

---

Recovery belongs to agents.

---

# 22. AUDIT REQUIREMENTS

Routing decisions should record:

Task

Selected Model

Reason

Complexity

Risk

Confidence

Outcome

---

Routing decisions should remain auditable.

---

# 23. SUCCESS CONDITIONS

Model Router succeeds when:

Correct Model Selected

Safety Maintained

Costs Controlled

Performance Acceptable

Privacy Preserved

---

# 24. FAILURE CONDITIONS

Model Router fails when:

Incorrect Model Selected

Unnecessary Escalation

Excessive Cost

Privacy Violations

Safety Compromised

---

# 25. FINAL DIRECTIVE

Select the smallest model capable of safely completing the task.

Optimize for correctness first.

Respect privacy.

Control costs.

Escalate only when justified.

Context determines model selection.