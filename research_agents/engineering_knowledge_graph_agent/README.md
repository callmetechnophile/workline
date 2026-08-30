# EngineeringKnowledgeGraphAgent (Agent #13)

**EngineeringKnowledgeGraphAgent** is Agent #13 of the WorkflowGuide AI multi-agent platform. It is the **central persistence, state management, and knowledge graph agent** responsible for converting the complete verified engineering lifecycle (Agents #1–#12) into a unified, queryable **SurrealDB knowledge graph** with strict multi-user project isolation.

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
```

---

## 2. Core Principles & Responsibilities

> [!IMPORTANT]
> **ACCURATE PERSISTENCE & TRACEABILITY.**  
> - Agent #13 does *not* redesign architectures, execute code, purchase parts, or override validation.  
> - It deterministically persists the complete engineering lifecycle into SurrealDB.  
> - Preserves historical versions using `SUPERSEDES` relations.  
> - Maintains strict multi-tenant project isolation (User A cannot access User B's project graph).

---

## 3. Unified Connected SurrealDB Graph

$$\text{USER} \longrightarrow \text{PROJECT} \longrightarrow \text{REQUIREMENTS} \longrightarrow \text{DECISIONS} \longrightarrow \text{ARCHITECTURE} \longrightarrow \text{COMPONENTS} \longrightarrow \text{BOM} \longrightarrow \text{TASKS} \longrightarrow \text{EXECUTION} \longrightarrow \text{TESTS} \longrightarrow \text{VERIFICATION}$$

### Key Graph Nodes
- `user`, `team`, `project`
- `requirement`, `research`, `engineering_decision`
- `architecture`, `subsystem`, `interface`, `component`
- `bom`, `bom_item`, `supplier`, `supplier_offer`, `procurement_plan`, `shipping_option`
- `implementation_plan`, `work_package`, `implementation_task`
- `execution`, `project_file`, `test`, `test_result`, `evidence`
- `validation`, `engineering_failure`, `agent`, `authorization`, `delegation`, `execution_receipt`
- `project_state`, `state_event`, `audit_event`

---

## 4. Deterministic Project State Machine

Allowed sequence:
$$\text{research} \longrightarrow \text{design} \longrightarrow \text{bom} \longrightarrow \text{procurement} \longrightarrow \text{validation} \longrightarrow \text{planning} \longrightarrow \text{implementation} \longrightarrow \text{qa} \longrightarrow \text{verified}$$

- Upstream validation/QA failure transitions the project to `blocked`.
- QA failure is *never* permitted to become `verified`.

---

## 5. Traceability & Impact Analysis Services

1. **Requirement Lineage Trace**:
   - Traces `Requirement` $\rightarrow$ `Decision` $\rightarrow$ `Architecture` $\rightarrow$ `Subsystem` $\rightarrow$ `Component` $\rightarrow$ `BOM` $\rightarrow$ `Task` $\rightarrow$ `Execution` $\rightarrow$ `Test` $\rightarrow$ `Evidence` $\rightarrow$ `Validation/QA`.
2. **Component Impact Analysis**:
   - Identifies all subsystems, interfaces, BOM line items, procurement plans, tasks, files, tests, and requirements impacted when a component changes or is unavailable.
3. **Requirement Impact Analysis**:
   - Identifies design decisions, subsystems, components, and tests requiring revalidation when a requirement is modified.
4. **Architecture Impact Analysis**:
   - Maps subsystem changes to affected interfaces, components, and task workflows.

---

## 6. CLI Usage & Commands

```bash
# Ingest project lifecycle into SurrealDB
python -m engineering_knowledge_graph_agent --demo

# Trace requirement lineage
python -m engineering_knowledge_graph_agent trace --requirement REQ-SAR-001 --project proj_sar_drone_001

# Analyze component impact
python -m engineering_knowledge_graph_agent impact --component 500-0771-01 --project proj_sar_drone_001

# Inspect current project state
python -m engineering_knowledge_graph_agent state --project proj_sar_drone_001

# Inspect project timeline
python -m engineering_knowledge_graph_agent timeline --project proj_sar_drone_001

# Export graph
python -m engineering_knowledge_graph_agent export --project proj_sar_drone_001 --format json
```

---

## 7. Automated Testing

```bash
pytest research_agents/engineering_knowledge_graph_agent/tests/ -v
```
