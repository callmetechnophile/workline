# EngineeringChangeControlAgent (Agent #16)

**EngineeringChangeControlAgent** is Agent #16 of the WorkflowGuide AI multi-agent platform. It operates as the **change control and version management authority** over the persistent SurrealDB knowledge graph (Agent #13) and lifecycle orchestrator (Agent #14).

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
USER
```

---

## 2. Core Principles & Controlled Lifecycle

> [!IMPORTANT]
> **CONTROLLED ENGINEERING CHANGE (ZERO SILENT MUTATION & ZERO DIRECT EXECUTION).**  
> - Every engineering modification is represented as an auditable `ChangeRequest`.  
> - Validated artifacts are **never overwritten**. New versions supersede older versions (`SUPERSEDES`).  
> - When an upstream artifact changes, dependent artifacts are marked **`STALE`** and previous QA/validation results are marked **`INVALIDATED`** (never deleted).  
> - **No Self-Approval**: Requesters cannot approve their own critical change requests.  
> - **Execution Separation**: Agent #16 defines change plans and routes them through Agent #14 $\rightarrow$ ArmorIQ $\rightarrow$ execution agents.

$$\text{REQUEST} \longrightarrow \text{CLASSIFY} \longrightarrow \text{IMPACT} \longrightarrow \text{RISK} \longrightarrow \text{APPROVAL} \longrightarrow \text{VERSION} \longrightarrow \text{AGENT \#14} \longrightarrow \text{ARMORIQ} \longrightarrow \text{IMPLEMENTATION} \longrightarrow \text{VALIDATION} \longrightarrow \text{QA} \longrightarrow \text{AGENT \#13} \longrightarrow \text{VERIFIED}$$

---

## 3. History-Preserving Forward Rollback

Rollback does **not** erase history or delete newer versions. Instead, a new forward version (e.g., `v4.0.0`) is created that restores the validated state of `v2.0.0` while superseding `v3.0.0`.

---

## 4. CLI Usage & Commands

```bash
# Full change control demo run
python -m engineering_change_control --demo

# Create a component change request
python -m engineering_change_control create \
    --project proj_sar_drone_001 \
    --type COMPONENT_CHANGE \
    --target 500-0771-01 \
    --title "Replace thermal sensor candidate" \
    --description "Upgrade FLIR Lepton 2.5 to 3.5"

# Inspect direct and indirect impact
python -m engineering_change_control impact --change CHANGE-001

# Approve a change request (independent approver)
python -m engineering_change_control approve --change CHANGE-001 --approver lead_engineer_002

# Forward rollback versioning
python -m engineering_change_control rollback \
    --artifact ARCH-001 \
    --target-version v1.0.0 \
    --current-version v2.0.0 \
    --approved-by lead_engineer_002
```

---

## 5. Artifact File Exports (5 Files)

1. `change_request.json`
2. `change_impact.json`
3. `change_risks.json`
4. `change_plan.json`
5. `change_report.md` (20-section Markdown report)

---

## 6. Automated Testing

```bash
pytest research_agents/engineering_change_control/tests/ -v
```
