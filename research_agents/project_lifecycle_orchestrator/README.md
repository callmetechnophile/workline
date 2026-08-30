# ProjectLifecycleOrchestrator (Agent #14)

**ProjectLifecycleOrchestrator** is Agent #14 of the WorkflowGuide AI multi-agent platform. It operates as the **project-level engineering lifecycle controller** that uses the persistent SurrealDB knowledge graph to continuously observe, evaluate, decide, authorize, delegate, verify, and persist the next valid engineering workflow action.

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
```

---

## 2. Core Principles & Responsibilities

> [!IMPORTANT]
> **DECISION + ORCHESTRATION LAYER (ZERO DIRECT EXECUTION).**  
> - Agent #14 decides **WHAT should happen next** and **WHICH agent should execute it**.  
> - It does *not* directly modify code, PCB, or BOM.  
> - It *never* bypasses Agent #9 validation, Agent #10 planning, Agent #11 execution, Agent #12 QA, ArmorIQ authorization, or human approvals.  
> - **Separation of Authorization**: Decision is *not* authorization. Cryptographic grants must be evaluated and issued by ArmorIQ.

---

## 3. Closed-Loop Lifecycle Controller

$$\text{OBSERVE} \longrightarrow \text{UNDERSTAND} \longrightarrow \text{DECIDE} \longrightarrow \text{AUTHORIZE} \longrightarrow \text{DELEGATE} \longrightarrow \text{EXECUTE} \longrightarrow \text{VERIFY} \longrightarrow \text{PERSIST} \longrightarrow \text{OBSERVE AGAIN}$$

1. **Observe**: Queries the persistent SurrealDB graph via `KnowledgeGraphService`.
2. **Understand**: Evaluates blockers, dependencies, and state machine invariants.
3. **Decide**: NextActionEngine computes the next deterministic workflow step.
4. **Authorize**: Requests scoped ArmorIQ delegation tokens for child agents.
5. **Delegate**: Dispatches work packages to specialized agents (Agents #1–#13).
6. **Verify**: Independent QA (Agent #12) evaluates evidence and test telemetry.
7. **Persist**: Graph persistence (Agent #13) stores nodes, relations, and state changes.

---

## 4. Deterministic State Machine

$$\text{RESEARCH} \longrightarrow \text{SYNTHESIS} \longrightarrow \text{ARCHITECTURE} \longrightarrow \text{BOM} \longrightarrow \text{PROCUREMENT} \longrightarrow \text{VALIDATION} \longrightarrow \text{PLANNING} \longrightarrow \text{IMPLEMENTATION} \longrightarrow \text{QA} \longrightarrow \text{VERIFIED}$$

* Critical failures or unmet prerequisites transition state to `BLOCKED`.
* Material architecture changes or high-risk actions transition state to `AWAITING_HUMAN`.
* **Loop Guard**: Halts automated retry after 3 identical failures and escalates to `AWAITING_HUMAN`.

---

## 5. Specialized Failure Routing & Revalidation

* **Architecture Failure (`ARCHITECTURE_CONFORMANCE_FAILURE`)**:  
  $\rightarrow$ Agent #6 (Architecture Review) $\rightarrow$ Agent #9 (Validation) $\rightarrow$ Agent #10 (Planning) $\rightarrow$ Agent #11 (Execution) $\rightarrow$ Agent #12 (QA)
* **BOM Failure (`BOM_CONFORMANCE_FAILURE`)**:  
  $\rightarrow$ Agent #8 (BOM Optimization) $\rightarrow$ Agent #9 (Validation) $\rightarrow$ Agent #10 (Planning) $\rightarrow$ Agent #11 (Execution) $\rightarrow$ Agent #12 (QA)
* **Test Failure (`TEST_FAILURE`)**:  
  $\rightarrow$ Agent #10 (Remediation Planning) $\rightarrow$ Agent #9 (Validation) $\rightarrow$ Agent #11 (Execution) $\rightarrow$ Agent #12 (QA)
* **Documentation-Only Changes**: Require zero engineering revalidation.

---

## 6. CLI Usage & Commands

```bash
# Full closed-loop demo run
python -m project_lifecycle_orchestrator --demo

# Inspect project status and next action
python -m project_lifecycle_orchestrator status --project PROJECT-001

# Determine next action based on QA verdict
python -m project_lifecycle_orchestrator next --project PROJECT-001 --qa-status FAILED --failure-type TEST_FAILURE

# Inspect engineering health
python -m project_lifecycle_orchestrator health --project PROJECT-001

# Inspect active blockers
python -m project_lifecycle_orchestrator blockers --project PROJECT-001

# Determine revalidation impact
python -m project_lifecycle_orchestrator impact --change-type COMPONENT --artifact 500-0771-01

# Approve human decision request
python -m project_lifecycle_orchestrator approve REQ-HUMAN-001
```

---

## 7. Artifact File Exports (8 Files)

1. `orchestration_run.json`
2. `project_health.json`
3. `next_action.json`
4. `decision_history.json`
5. `blockers.json`
6. `human_requests.json`
7. `state_transitions.json`
8. `orchestration_report.md` (16 sections)

---

## 8. Automated Testing

```bash
pytest research_agents/project_lifecycle_orchestrator/tests/ -v
```
