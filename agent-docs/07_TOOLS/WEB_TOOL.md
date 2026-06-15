# WEB_TOOL.md

Version: 1.0

Status: Active

Authority Level: High

Related Documents:

- TOOL_REGISTRY.md
- PERMISSION_SYSTEM.md
- SAFETY_RULES.md
- MODEL_ROUTER.md
- MEMORY_RETRIEVAL.md

---

# 1. PURPOSE

This document defines the Web Tool used by CAMera.

The Web Tool provides external information retrieval, research, verification, benchmarking, documentation lookup, and evidence gathering capabilities.

The Web Tool is a research instrument.

It does not make decisions.

---

# 2. CORE PHILOSOPHY

The Web Tool gathers information.

Agents analyze information.

The Planner synthesizes research.

The Manager governs execution.

The Web Tool should prioritize evidence over assumptions.

---

# 3. RESPONSIBILITIES

The Web Tool may:

- Search the Web
- Retrieve Documentation
- Retrieve Research Papers
- Retrieve GitHub Discussions
- Retrieve GitHub Issues
- Retrieve Community Discussions
- Retrieve Security Advisories
- Retrieve Technical Articles
- Retrieve Benchmark Data

---

# 4. NON-RESPONSIBILITIES

The Web Tool is not responsible for:

- Decision Making
- Architecture Decisions
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

Research Strategy Selection

↓

Web Tool

↓

Source Analysis

↓

Result Synthesis

↓

Agent

---

# 6. REQUIRED CAPABILITIES

Examples:

web_search

documentation_lookup

research_lookup

security_lookup

benchmark_lookup

---

Operations require matching capabilities.

---

# 7. RESEARCH PHILOSOPHY

CAMera should not simply search.

CAMera should:

Classify Problem

↓

Select Research Strategy

↓

Gather Evidence

↓

Analyze Sources

↓

Generate Recommendation

---

# 8. SOURCE EVALUATION

Sources should be evaluated using:

Authority

Recency

Evidence Quality

Corroboration

Relevance

Bias Risk

---

# 9. RESEARCH STRATEGIES

Research strategy depends on problem type.

Different questions require different evidence.

---

# 10. BUG INVESTIGATION

Priority:

GitHub Issues

↓

GitHub Discussions

↓

Community Discussions

↓

Stack Overflow

↓

Official Documentation

---

Reason:

Bugs are often discovered before documentation updates.

---

# 11. FRAMEWORK USAGE

Priority:

Official Documentation

↓

Official Examples

↓

Official Repositories

↓

Community Examples

---

Reason:

Framework authors define intended usage.

---

# 12. RESEARCH QUESTIONS

Priority:

Research Papers

↓

Technical Reports

↓

Official Documentation

↓

Expert Analysis

---

Reason:

Evidence quality is critical.

---

# 13. SECURITY INVESTIGATION

Priority:

Security Advisories

↓

Vendor Documentation

↓

Security Researchers

↓

Community Reports

---

Reason:

Security requires authoritative and current information.

---

# 14. ARCHITECTURE RESEARCH

Priority:

Official Documentation

↓

Engineering Blogs

↓

Case Studies

↓

Community Discussions

---

Reason:

Real-world implementation experience matters.

---

# 15. SOURCE CONFLICT RESOLUTION

Conflicting sources should not be ignored.

CAMera should:

Identify Conflict

↓

Evaluate Sources

↓

Estimate Confidence

↓

Provide Recommendation

↓

Expose Tradeoffs

---

# 16. SOURCE EVALUATION FACTORS

Evaluate:

Authority

Recency

Evidence

Benchmarks

Community Experience

Project Context

Risk Profile

---

No single factor should dominate all decisions.

---

# 17. RECOMMENDATION PHILOSOPHY

CAMera should not blindly trust:

- Authority
- Community Consensus
- Benchmarks

Recommendations should be context dependent.

---

# 18. RESEARCH OUTPUT FORMAT

Research results should contain:

Finding

Confidence

Supporting Evidence

Conflicting Evidence

Recommendation

Tradeoffs

---

# 19. CONFIDENCE LEVELS

High

Medium

Low

---

# 20. HIGH CONFIDENCE

Characteristics:

Multiple Strong Sources

Strong Agreement

Recent Evidence

---

# 21. MEDIUM CONFIDENCE

Characteristics:

Minor Disagreement

Limited Contradictions

Moderate Evidence

---

# 22. LOW CONFIDENCE

Characteristics:

Weak Evidence

Major Conflicts

Limited Sources

Outdated Information

---

# 23. LOW CONFIDENCE POLICY

Low confidence findings should not be hidden.

CAMera should:

Return Findings

Explain Uncertainty

Identify Research Gaps

Provide Confidence Score

Suggest Next Steps

---

# 24. RESEARCH ESCALATION

Planner may initiate deeper research when:

Decision Impact High

Risk High

Evidence Weak

Conflicts Significant

---

Escalation should be proportional to importance.

---

# 25. BENCHMARK ANALYSIS

Benchmarks should be evaluated using:

Methodology

Sample Size

Environment

Recency

Reproducibility

---

Benchmark results should not be accepted blindly.

---

# 26. DOCUMENTATION ANALYSIS

Documentation should be evaluated using:

Authority

Version

Maintenance Status

Relevance

---

Documentation may become outdated.

---

# 27. COMMUNITY ANALYSIS

Community sources may provide:

Practical Experience

Workarounds

Emerging Issues

Operational Insights

---

Community consensus is evidence, not authority.

---

# 28. SECURITY RESEARCH

Security findings should prioritize:

Accuracy

Recency

Verification

Impact Assessment

---

Potential security risks should be highlighted.

---

# 29. AUDIT REQUIREMENTS

Research activity should record:

Agent

Query

Sources Consulted

Confidence

Recommendation

Timestamp

---

Research should remain auditable.

---

# 30. SUCCESS CONDITIONS

Web Tool succeeds when:

Relevant Information Retrieved

Sources Evaluated Correctly

Conflicts Identified

Confidence Estimated

Recommendations Justified

---

# 31. FAILURE CONDITIONS

Web Tool fails when:

Sources Misrepresented

Conflicts Hidden

Confidence Misstated

Evidence Ignored

Recommendations Unsupported

---

# 32. FINAL DIRECTIVE

Gather evidence.

Evaluate sources.

Expose uncertainty.

Explain tradeoffs.

Provide recommendations.

Support informed decisions.

The Web Tool gathers knowledge.

Agents determine what to do with it.