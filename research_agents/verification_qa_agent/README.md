# VerificationQAAgent (Agent #12)

**VerificationQAAgent** is Agent #12 of the WorkflowGuide AI multi-agent platform. It is an **autonomous, independent verification and QA agent** that verifies whether the implementation produced by Agent #11 actually satisfies all approved engineering requirements, architecture flows, BOM components, test suites, and security invariants under **cryptographic ArmorIQ authority**.

---

## 1. Multi-Agent Pipeline Position

```
User
  ↓
Research Orchestrator
  ↓
Agent #1 — ResearchPaperAgent (Academic Research via Freephdlabor)
  ↓
Agent #2 — WebResearchAgent (Engineering Web Evidence via Tavily + Anakin)
  ↓
Agent #3 — DocumentProcessingAgent (PDF/HTML Normalization, Chunks, Facts, Entities)
  ↓
Agent #4 — DeepResearchAgent (Amazon Bedrock Cross-Source Reasoning & Evidence Synthesis)
  ↓
Agent #5 — EngineeringSynthesisAgent (Requirements, Findings, Decisions, Risks)
  ↓
Agent #6 — EngineeringArchitectureAgent (Subsystems, Interfaces, Power, Flows, Graphs)
  ↓
Agent #7 — ComponentPlanningAgent (Engineering BOM, Exact Components, Validation)
  ↓
Agent #8 — BOMOptimizationAgent (BOM Optimization, Suppliers, Landed Cost, Logistics)
  ↓
Agent #9 — EngineeringValidationAgent (Engineering Quality Gate, Design Rules, Verdict)
  ↓
Agent #10 — ProjectExecutionAgent (Work Packages, Task Breakdown, Scheduling)
  ↓
Agent #11 — EngineeringExecutionAgent (Cryptographic ArmorIQ Scoped Implementation)
  ↓
Agent #12 — VerificationQAAgent (Independent Verification & Autonomous QA Quality Gate)
```

---

## 2. Core Independence Principle

> [!IMPORTANT]
> **NEVER BLINDLY TRUST AGENT #11 CLAIMS.**  
> - "Task completed" is never accepted as proof of correctness.  
> - "Tests passed" is never accepted as proof of complete system correctness.  
> - Agent #12 independently inspects the file tree, executes test suites, performs static security analysis, checks data/control flow conformance, audits cryptographic ArmorIQ receipts, and requires objective evidence for every `PASS`.

---

## 3. Multi-Domain Verification Pipeline

```
Agent #11 Execution Output
        ↓
Repository & File Tree Inspection
        ↓
Actual vs Expected Change Verification
        ↓
Task & Acceptance Criteria Verification
        ↓
Static Security & Secret Scanning (with Masking)
        ↓
Pytest Unit, Integration & Regression Test Execution
        ↓
Architecture & BOM Conformance Evaluation
        ↓
Requirement-to-Evidence Traceability Lineage
        ↓
ArmorIQ Cryptographic Receipt Audit
        ↓
Quality Gate Final Verdict & Prescriptive Correction Report
```

---

## 4. Quality Gate Verdicts & Blocking Conditions

| Verdict | Definition |
|---|---|
| `VERIFIED` | 100% of mandatory requirements, tests, security, and conformance checks have verified evidence. |
| `VERIFIED_WITH_WARNINGS` | Mandatory requirements pass; non-blocking items (e.g. optional tests skipped) flagged. |
| `FAILED` | Critical requirement fails, security vulnerability found, unauthorized modification, architecture/BOM conflict, or test failure. |
| `INCOMPLETE` | Verification could not complete due to missing physical hardware/environment without defined simulation. |
| `BLOCKED` | Upstream validation gate (Agent #9) was `BLOCKED`. |

---

## 5. Security & Prompt Injection Scanner

Scans all implementation files for:
- Hardcoded API keys (AWS, OpenAI, Anthropic, generic tokens) — **automatically masked in all reports**.
- Private keys and passwords.
- Command injection (`system("rm -rf ...")`, `curl`, `wget`).
- Prompt injection vectors (`ignore previous instructions and`).

---

## 6. 11-File Artifact Export (Section 63)

When invoked with `--output <directory>`, the agent exports:

1. `verification_result.json`: Complete machine-readable QA result.
2. `verification_report.md`: Publication-ready 24-section Markdown report.
3. `requirement_matrix.json`: Traceability matrix across all requirements.
4. `test_results.json`: Unit/integration test telemetry and exit codes.
5. `coverage_matrix.json`: Requirement-to-evidence coverage matrix.
6. `security_report.json`: Security findings with masked snippets.
7. `architecture_conformance.json`: Architecture flow compliance evaluation.
8. `bom_conformance.json`: BOM component substitution audit.
9. `authorization_verification.json`: ArmorIQ receipt and scope audit.
10. `verification_traceability.json`: Unbroken lineage records.
11. `correction_report.json`: Prescriptive remediation requests for any defects.

---

## 7. CLI Usage & Development Mode

```bash
# Run SAR drone QA verification demo
python -m verification_qa_agent --demo

# Run dry-run verification
python -m verification_qa_agent \
    --plan ./implementation_plan.json \
    --execution ./execution_result.json \
    --dry-run

# Run test-only verification
python -m verification_qa_agent \
    --plan ./implementation_plan.json \
    --execution ./execution_result.json \
    --tests-only

# Run security-only scan
python -m verification_qa_agent \
    --plan ./implementation_plan.json \
    --execution ./execution_result.json \
    --security-only
```

---

## 8. Automated Testing

```bash
pytest research_agents/verification_qa_agent/tests/ -v
```
