# EngineeringCopilotAgent (Agent #15)

**EngineeringCopilotAgent** is Agent #15 of the WorkflowGuide AI multi-agent platform. It operates as the **natural-language engineering copilot and conversational interface** over the persistent SurrealDB knowledge graph (Agent #13) and lifecycle orchestrator (Agent #14).

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
USER
```

---

## 2. Core Principles & Responsibilities

> [!IMPORTANT]
> **READ + EXPLAIN + ANALYZE + RECOMMEND (ZERO DIRECT EXECUTION).**  
> - Copilot answers questions, traces dependencies, analyzes impact, and explains engineering decisions.  
> - It does *not* directly modify code, PCB, BOM, purchase components, or execute shell commands.  
> - For all action requests (e.g., "Run TASK-042", "Deploy this"): creates an `ActionProposal` and routes it to Agent #14 (`ProjectLifecycleOrchestrator`) $\rightarrow$ ArmorIQ authorization $\rightarrow$ authorized execution agent.  
> - **Separation of Authorization**: Copilot never grants authorization or bypasses ArmorIQ.

---

## 3. Evidence-First Grounding & Zero Hallucination

$$\text{GRAPH} \longrightarrow \text{EVIDENCE} \longrightarrow \text{REASONING} \longrightarrow \text{ANSWER}$$

* **Evidence Grounding**: Factual statements cite graph node IDs (`REQ-xxx`, `COMP-xxx`, `DEC-xxx`, `TEST-xxx`).
* **Unknown Handling**: Unverified properties return `UNKNOWN` with missing evidence rather than hallucinations.
* **Conflict & Stale Awareness**: Clearly identifies `STALE` or `INVALIDATED` draft versions (e.g., unvalidated draft V3 vs validated V2).

---

## 4. Action Proposal Workflow

$$\text{USER} \longrightarrow \text{COPILOT} \longrightarrow \text{ACTION PROPOSAL} \longrightarrow \text{AGENT \#14} \longrightarrow \text{ARMORIQ} \longrightarrow \text{AUTHORIZED AGENT} \longrightarrow \text{QA} \longrightarrow \text{GRAPH}$$

* Destructive or high-impact actions (deletion, deployment, financial ops) flag `requires_human_approval=True`.

---

## 5. CLI Usage & Commands

```bash
# Full evidence-grounded demonstration
python -m engineering_copilot --demo

# Ask an engineering question
python -m engineering_copilot ask --project proj_sar_drone_001 --question "Why was this MCU selected?"

# Trace requirement lineage
python -m engineering_copilot trace --project proj_sar_drone_001 --requirement REQ-SAR-001

# Analyze component impact
python -m engineering_copilot impact --project proj_sar_drone_001 --component 500-0771-01

# Compare BOM versions
python -m engineering_copilot compare --project proj_sar_drone_001 --version-a V1 --version-b V2

# Check project status & health
python -m engineering_copilot status --project proj_sar_drone_001

# Query next recommended action
python -m engineering_copilot next --project proj_sar_drone_001
```

---

## 6. Artifact File Exports (7 Files)

1. `copilot_response.json`
2. `project_summary.json`
3. `traceability_response.json`
4. `impact_analysis.json`
5. `comparison.json`
6. `conversation.json`
7. `action_proposals.json`

---

## 7. Automated Testing

```bash
pytest research_agents/engineering_copilot/tests/ -v
```
