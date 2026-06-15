# DATA_FLOW.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

* SYSTEM_ARCHITECTURE.md
* AGENT_TOPOLOGY.md
* AGENT_CONSTITUTION.md

---

# 1. PURPOSE

This document defines how information moves throughout CAMera.

Goals:

* Traceability
* Reliability
* Debuggability
* Knowledge preservation

Every important piece of information must have:

* Source
* Owner
* Destination
* Lifecycle

---

# 2. CORE DATA FLOW

User Request
↓
Manager Agent
↓
Architect Agent
↓
Planner Agent
↓
Coder Agent
↓
Tester Agent
↓
Debugger Agent (if needed)
↓
Reviewer Agent
↓
Manager Agent
↓
User

Memory Agent may participate at any stage.

---

# 3. REQUEST FLOW

Input:

User Goal

Examples:

* Build a website
* Debug an API
* Design architecture
* Explain a concept

Owner:

Manager Agent

Responsibilities:

* Understand request
* Classify request
* Route request

Output:

Task Definition

---

# 4. ARCHITECTURE FLOW

Input:

Task Definition

Owner:

Architect Agent

Responsibilities:

* Analyze requirements
* Design architecture
* Identify risks

Output:

Architecture Specification

Destination:

Planner Agent

---

# 5. RESEARCH FLOW

Input:

Architecture Specification

Owner:

Planner Agent

Responsibilities:

* Gather documentation
* Research technologies
* Compare options
* Validate assumptions

Primary Resources:

* Firecrawl MCP
* MarkItDown MCP
* temp_websearch_skill
* agent-browser

Output:

Research Package

---

# 6. KNOWLEDGE EVALUATION FLOW

Input:

Research Package

Owner:

Planner Agent

Responsibilities:

* Evaluate usefulness
* Determine long-term value
* Classify information

Decision:

Store
or
Discard

---

# 7. KNOWLEDGE STORAGE FLOW

If information is valuable:

Planner Agent
↓
Memory Agent
↓
Memory Evaluation

Memory Agent determines:

Global Memory
or
Project Memory

---

# 8. MEMORY STORAGE CRITERIA

Store:

* Architecture decisions
* Major lessons
* User preferences
* Important discoveries
* Successful workflows
* Reusable solutions

Do Not Store:

* Temporary searches
* Trivial facts
* Duplicate information
* Low-value observations

---

# 9. IMPLEMENTATION FLOW

Input:

Approved Plan

Owner:

Coder Agent

Responsibilities:

* Create code
* Refactor code
* Implement features

Output:

Implementation Package

Destination:

Tester Agent

---

# 10. TESTING FLOW

Input:

Implementation Package

Owner:

Tester Agent

Responsibilities:

* Execute tests
* Validate requirements
* Check regressions

Output:

Validation Report

---

# 11. FAILURE FLOW

If failures occur:

Tester Agent
↓
Debugger Agent

Debugger Responsibilities:

* Root cause analysis
* Impact analysis
* Recovery recommendations

Output:

Debug Report

Destination:

Coder Agent

---

# 12. REVIEW FLOW

Input:

Validated Implementation

Owner:

Reviewer Agent

Responsibilities:

* Security review
* Quality review
* Maintainability review

Output:

Review Report

Destination:

Manager Agent

---

# 13. COMPLETION FLOW

Manager receives:

* Architecture Results
* Research Results
* Test Results
* Review Results

Manager evaluates:

Success Criteria

Completion Criteria

Constitution Compliance

Output:

Completion Decision

---

# 14. MCP DATA FLOW

Firecrawl
↓
Raw Documentation

MarkItDown
↓
Structured Markdown

Planner
↓
Knowledge Evaluation

Memory Agent
↓
Storage Decision

Memory
↓
Future Retrieval

---

# 15. TOOL DATA FLOW

Agent
↓
Tool Request

Tool
↓
Execution

Tool
↓
Result

Agent
↓
Interpretation

Manager
↓
Decision

Tools do not make decisions.

Agents make decisions.

---

# 16. MEMORY RETRIEVAL FLOW

Task Starts
↓
Manager
↓
Memory Agent

Memory Agent Searches:

Global Memory

Project Memory

Relevant Knowledge

Output:

Context Package

Destination:

Requesting Agent

---

# 17. USER FEEDBACK FLOW

User Feedback
↓
Manager

Manager Classifies:

Preference

Correction

New Requirement

Improvement

Knowledge

Important information may be stored.

---

# 18. PERFORMANCE DATA FLOW

Benchmark Skill
↓
Metrics

Metrics
↓
Manager

Manager
↓
Evaluation

If Regression Exists:

Debugger Investigation

User Notification

---

# 19. AUDITABILITY RULE

Every major decision must be traceable.

Requirements:

Source

Reason

Evidence

Decision Maker

Outcome

Storage Location

---

# 20. FINAL DATA FLOW DIRECTIVE

Information should move intentionally.

Knowledge should be preserved selectively.

Every significant decision must be explainable, traceable, and recoverable.
