# EngineeringVerificationAgent (Agent #18)

**EngineeringVerificationAgent** is Agent #18 of the WorkflowGuide AI multi-agent platform. It operates as the **engineering verification, test execution coordination, measurement/simulation evidence engine, and requirement traceability authority** across the platform.

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
  ↓
Agent #13 — EngineeringKnowledgeGraphAgent (SurrealDB Graph & Project State Machine)
  ↓
Agent #14 — ProjectLifecycleOrchestrator (Autonomous Project Orchestrator & Lifecycle Manager)
  ↓
Agent #15 — EngineeringCopilotAgent (Natural-Language Engineering Copilot & Interface)
  ↓
Agent #16 — EngineeringChangeControlAgent (Change Control & Version Management Authority)
  ↓
Agent #17 — EngineeringComplianceAgent (Deterministic Engineering Compliance & Safety Gatekeeper)
  ↓
Agent #18 — EngineeringVerificationAgent (Engineering Verification, Test & Evidence Engine)
  ↓
USER
```

---

## 2. Core Principles & Evidence Integrity

> [!IMPORTANT]
> **THE EVIDENCE ENGINE (ZERO FABRICATION & ZERO DIRECT EXECUTION).**  
> - Answers: **"WHAT EVIDENCE PROVES THAT THIS WORKS?"**  
> - Strictly distinguishes: `DESIGNED`, `IMPLEMENTED`, `TESTED`, `VERIFIED`, `VALIDATED`, `COMPLIANT`.  
> - Never invents measurements, test results, or simulations. Unexecuted tests remain `PLANNED` or `NOT_EXECUTED` (never `PASS`).  
> - Missing hardware fixtures cause tests to be marked `BLOCKED` (never `PASS`).  
> - All executable test operations are registered, scoped, and authorized through **ArmorIQ**.  
> - **Change Invalidation**: When an upstream component/architecture changes, dependent tests and evidence are marked `INVALIDATED` (never deleted) and re-verification is scheduled.

$$\text{REQUIREMENT} \longrightarrow \text{METHOD} \longrightarrow \text{TEST} \longrightarrow \text{EXECUTION} \longrightarrow \text{RESULT} \longrightarrow \text{EVIDENCE} \longrightarrow \text{VERIFIED}$$

---

## 3. Verification Methods (16 Methods)

1. `ANALYSIS`
2. `INSPECTION`
3. `TEST`
4. `MEASUREMENT`
5. `SIMULATION`
6. `CALCULATION`
7. `REVIEW`
8. `DEMONSTRATION`
9. `STATIC_ANALYSIS`
10. `DYNAMIC_TEST`
11. `HARDWARE_TEST`
12. `SOFTWARE_TEST`
13. `INTEGRATION_TEST`
14. `SYSTEM_TEST`
15. `ACCEPTANCE_TEST`
16. `PCB_VERIFICATION`

---

## 4. CLI Usage & Commands

```bash
# Full verification demo run
python -m engineering_verification --demo

# Inspect verification status and metrics
python -m engineering_verification status --project proj_sar_drone_001

# Run an authorized test
python -m engineering_verification run --project proj_sar_drone_001 --test TEST-SAR-001

# View requirement verification coverage
python -m engineering_verification coverage --project proj_sar_drone_001

# View requirement-to-evidence matrix
python -m engineering_verification matrix --project proj_sar_drone_001

# Calculate change re-verification impact
python -m engineering_verification reverify \
    --project proj_sar_drone_001 \
    --target sensor_core
```

---

## 5. Artifact File Exports (6 Files)

1. `verification_plan.json`
2. `verification_report.json`
3. `verification_matrix.json`
4. `test_results.json`
5. `evidence_index.json`
6. `verification_report.md` (18-section Markdown report)

---

## 6. Automated Testing

```bash
pytest research_agents/engineering_verification/tests/ -v
```
