# EngineeringComplianceAgent (Agent #17)

**EngineeringComplianceAgent** is Agent #17 of the WorkflowGuide AI multi-agent platform. It operates as the **deterministic engineering compliance gatekeeper, design-rule checker, and safety constraint validator** over the persistent SurrealDB knowledge graph (Agent #13), lifecycle orchestrator (Agent #14), change-control authority (Agent #16), and engineering validation agent (Agent #9).

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
USER
```

---

## 2. Core Principles & Gatekeeper Integrity

> [!IMPORTANT]
> **DETERMINISTIC GATEKEEPER (ZERO FABRICATION & ZERO DIRECT EXECUTION).**  
> - Answers: **DOES THIS DESIGN COMPLY?** based strictly on explicit requirements, constraints, validated specifications, and verified evidence.  
> - Never invents standards, regulatory limits, or compliance claims. If missing $\rightarrow$ `UNKNOWN` or `COMPLIANCE_UNDETERMINED` (never converted to `PASS`).  
> - Critical failures block workflow (`BLOCK`).  
> - **Waivers Do Not Disguise Failures**: An active approved waiver yields `ALLOW_WITH_APPROVED_EXCEPTION`, while the underlying result remains `FAIL`. Expired waivers revert the gate to `BLOCK` or `REVIEW_REQUIRED`.  
> - **Change Control Integration**: When an upstream component/architecture changes, existing compliance results dependent on that artifact are marked `INVALIDATED` (never deleted).

$$\text{REQUIREMENT} \longrightarrow \text{RULE} \longrightarrow \text{ARTIFACT} \longrightarrow \text{CHECK} \longrightarrow \text{EVIDENCE} \longrightarrow \text{RESULT} \longrightarrow \text{COMPLIANCE GATE}$$

---

## 3. Compliance Domains (18 Domains)

1. `ELECTRICAL`
2. `ELECTRONICS`
3. `POWER`
4. `THERMAL`
5. `MECHANICAL`
6. `SOFTWARE`
7. `FIRMWARE`
8. `COMMUNICATION`
9. `INTERFACE`
10. `BOM`
11. `PROCUREMENT`
12. `MANUFACTURING`
13. `ENVIRONMENTAL`
14. `SAFETY`
15. `SECURITY`
16. `PROJECT_REQUIREMENTS`
17. `CUSTOM_DESIGN_RULES`
18. `APPLICABLE_STANDARDS`

---

## 4. CLI Usage & Commands

```bash
# Full compliance demo run
python -m engineering_compliance --demo

# Evaluate project compliance and gate status
python -m engineering_compliance check --project proj_sar_drone_001

# View requirement-to-compliance matrix
python -m engineering_compliance matrix --project proj_sar_drone_001

# Evaluate single component
python -m engineering_compliance component --project proj_sar_drone_001 --component 500-0771-01

# Create an approved temporary waiver
python -m engineering_compliance waiver \
    --project proj_sar_drone_001 \
    --rule RULE-ELEC-01 \
    --artifact component:500-0771-01 \
    --reason "Temporary lab supply variance" \
    --approved-by safety_officer_001
```

---

## 5. Artifact File Exports (6 Files)

1. `compliance_summary.json`
2. `compliance_results.json`
3. `compliance_matrix.json`
4. `compliance_waivers.json`
5. `compliance_gate.json`
6. `compliance_report.md` (25-section Markdown report)

---

## 6. Automated Testing

```bash
pytest research_agents/engineering_compliance/tests/ -v
```
